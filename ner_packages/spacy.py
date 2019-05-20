#!/usr/bin/env python3
import threading
import spacy
import en_core_web_sm
import nl_core_news_sm
import it_core_news_sm

from multiNER.named_entity_kit import NamedEntity

class Spacy(threading.Thread):
    '''
        Wrapper for Spacy.

        https://spacy.io/
       
    '''    
    nlp_spacy = None

    def __init__(self, language='en', text_input=''):
        threading.Thread.__init__(self)        
        self.text_input = text_input
        self.set_language(language)
        self.result = []


    def set_language(self, language):
        if (language == 'en'):
            self.nlp_spacy = en_core_web_sm.load()
        elif (language == 'nl'):
            self.nlp_spacy = nl_core_news_sm.load()
        elif (language == 'it'):
            self.nlp_spacy = it_core_news_sm.load()
        else:
            raise ValueError('language {0} is not supported'.format(language))
    

    def run(self):
        if not self.text_input:
            return

        data = self.collect_data()
        self.result = self.parse_response(data)


    def collect_data(self):        
        try:
            return self.nlp_spacy(self.text_input)
        except Exception as e:
            print('spacy error')
            print(e)
            pass

    
    def parse_response(self, data):
        entities = []
        
        for ent in data.ents:
            type = self.parse_type(ent.label_)
            ne = NamedEntity(ent.text, "spacy", ent.start_char, type)
            entities.append(ne)

        return entities

    
    def parse_type(self, spacy_type):        
        if spacy_type == 'PERSON':
            return 'PERSON'
        if spacy_type == 'LOC':
            return 'LOCATION'
        if spacy_type == 'ORG':
            return 'ORGANIZATION'
        return 'OTHER'


    def join(self):
        threading.Thread.join(self)
        return self.result
    