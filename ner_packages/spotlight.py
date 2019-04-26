#!/usr/bin/env python3
import threading
import requests

from .named_entity import NamedEntity


class Spotlight(threading.Thread):
    '''
        Wrapper for DBpedia-Spotlight.

        https://www.dbpedia-spotlight.org/        
    '''

    def __init__(self, url, timeout, language='en', text_input='', confidence='0.9'):
        threading.Thread.__init__(self)
        self.url = url
        self.timeout = timeout
        self.language = language
        self.text_input = text_input
        self.confidence = confidence


    def run(self):
        self.result = []

        if self.text_input is None:
            return
        
        data = self.collect_data
        self.result = self.parse_response(data)

    
    def collect_data(self):
        header = {"Accept": "application/json"}
        params = {'text': self.text_input, 'confidence': str(self.confidence)}

        done = False
        retry = 0
        max_retry = 10

        while not done and retry < max_retry:
            try:
                response = requests.get(self.url,
                                        params=params,
                                        headers=header,
                                        timeout=self.timeout)

                data = response.json()
                done = True
            except Exception as e:
                print('spotlight error:')
                print(e)
                data = []
                retry += 1

        return data


    def parse_response(self, data):
        entities = []

        if data and data.get('Resources'):
            for item in data.get('Resources'):
                self.parse_type(item)
                ne = {}
                ne = NamedEntity(text=item.get('@surfaceForm'), source="spotlight",
                                 position=int(item.get('@offset')), type=self.parse_type(item))
                entities.append(ne)

        return entities
        

    def parse_type(self, item):
        if "location" in item.get("@types").lower():
            return "LOCATION"
        else:
            return "OTHER"

    def join(self):
        threading.Thread.join(self)
        return self.result
