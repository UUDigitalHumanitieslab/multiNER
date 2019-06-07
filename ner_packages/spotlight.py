#!/usr/bin/env python3
import threading
import requests
import unicodedata

from multiNER.named_entity_kit import NamedEntity


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
        self.text_input = self.strip_accents(text_input)
        self.confidence = confidence

    def run(self):
        self.result = []

        if self.text_input is None:
            return
        
        self.result = self.collect_entities(self.text_input)

    def strip_accents(self, text):
        '''
        Strip the accent from the strip, because Spotlight can't cope with e aigu (é).
        See the tests also. 
        Courtesy of https://stackoverflow.com/a/44433664
        '''
        try:
            text = unicode(text, 'utf-8')
        except NameError:  # unicode is a default on python 3
            pass

        text = unicodedata.normalize('NFD', text)\
            .encode('ascii', 'ignore')\
            .decode("utf-8")

        return str(text)

    def collect_entities(self, text):
        entities = []
        data = self.collect_data(text)
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
                response = requests.post(self.url,
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
        types = item.get("@types").lower()

        if "location" in types:
            return "LOCATION"
        if "person" in types:
            return "PERSON"
        if "organization" in types or "organisation" in types:
            return "ORGANIZATION"
        return "OTHER"

    def join(self):
        threading.Thread.join(self)
        return self.result
