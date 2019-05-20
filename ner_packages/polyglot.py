#!/usr/bin/env python3
import ast
import threading
from polyglot.text import Text

from multiNER.named_entity_kit import NamedEntity


class Polyglot(threading.Thread):
    '''
        Wrapper for Polyglot.

        http://polyglot.readthedocs.io/en/latest/index.html

    '''

    def __init__(self, language='en', text_input=''):
        threading.Thread.__init__(self)
        self.language = language
        self.text_input = text_input
        self.result = []


    def run(self):
        if not self.text_input:
            return
            
        data = self.collect_data()
        polyglot_entities = self.parse_response(data)
        self.result = self.convert(polyglot_entities)
        

    def collect_data(self):        
        try:
            return Text(self.text_input, hint_language_code=self.language)
        except Exception as e:
            print('polyglot error:')
            print(e)

    
    def parse_response(self, data):
        entities = []

        for entity in data.entities:
            entities.append({'text': entity._collection[0], 'type': self.parse_type(entity.tag)})

        return entities

    
    '''
    Calculate position and create NamedEntity instances
    '''
    def convert(self, polyglot_entities):
        named_entities = []
        
        offset = 0
        for pge in polyglot_entities:
            text = pge["text"]
            pos = self.text_input[offset:].find(text)
            position = pos + offset
            offset += pos + len(text)
            
            ne = NamedEntity(text, "polyglot", position, pge['type'])
            named_entities.append(ne)
        
        return named_entities

    
    def parse_type(self, polyglot_type):        
        if polyglot_type == 'I-PER':
            return 'PERSON'
        if polyglot_type == 'I-LOC':
            return 'LOCATION'
        if polyglot_type == 'I-ORG':
            return 'ORGANIZATION'
        return "OTHER"


    def join(self):
        threading.Thread.join(self)
        return self.result
