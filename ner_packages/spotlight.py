#!/usr/bin/env python3
import threading
import requests

from .named_entity import NamedEntity

from textwrap import wrap


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
        
        text_chunks = self.get_spotlight_compatible_chunks(self.text_input)        
        self.result = self.collect_entities(text_chunks)

    
    def collect_entities(self, text_chunks):
        entities = []
        
        for chunk in text_chunks:
            data = self.collect_data(chunk)
            entities.extend(self.parse_response(data))

        return entities        

    
    def collect_data(self, text):
        header = {"Accept": "application/json"}
        params = {'text': text, 'confidence': str(self.confidence)}

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

    
    '''
    Spotlight receives the text as a parameter in the url. Therefore the max_length is limited to around 7000 characters
    This method cuts the text into pieces that the Spotlight API can handle.
    '''
    def get_spotlight_compatible_chunks(self, text, chunk_length = 7000):
        return wrap(text, chunk_length)


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
