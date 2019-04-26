#!/usr/bin/env python3
import telnetlib
from lxml import etree
import threading

from .named_entity import NamedEntity


class Stanford(threading.Thread):
    '''
        Wrapper for Stanford.

        https://nlp.stanford.edu/software/CRF-NER.shtml        
    '''

    def __init__(self, host, port, timeout, language='en', text_input=''):                
        threading.Thread.__init__(self)
        self.host = host
        self.timeout = timeout
        self.text_input = text_input
        self.port = port
        self.language = language
        
        

    def run(self):        
        self.result = []

        if self.text_input is None: return

        data = self.collect_data()
        stanford_entities = self.parse_response(data)        
        self.result = self.convert(stanford_entities)


    def collect_data(self):
        text = self.text_input.replace('\n', ' ')

        done = False
        retry = 0
        max_retry = 10

        while not done and retry < max_retry:
            try:
                conn = telnetlib.Telnet(host=self.host, port=self.port, timeout=self.timeout)
                done = True
            except Exception as e:
                print("stanford error:")
                print(e)
                retry += 1
            
        if not done:
            self.result = {"stanford": []}
            return

        text = text.encode('utf-8') + b'\n'
        conn.write(text)
        data = conn.read_all().decode('utf-8')        
        conn.close()

        return data



    '''
    Stanford NER inserts XML tags around the entities it finds. For example: '<B-LOC>Utrecht</B-LOC> en <B-LOC>Gouda</B-LOC>'
    If an entity consist of multiple parts, it becomes somthing like this: '<B-PER>Jelte</B-PER> <I-PER>van Boheemen</I-PER>'
    This method parses the response into dictionaries (note that these do not yet include position information)
    '''
    def parse_response(self, data):
        entities = []

        data = etree.fromstring('<root>' + data + '</root>')

        previous_item = None
        
        for item in data.iter():
            if not item.tag == 'root':
                if not self.is_multitag_item(item, previous_item):
                    entities.append({"text": item.text, "type": self.translate(item.tag)})
                    previous_item = item
                else: # this entity consists of two tags, update previous item
                    entities[-1]['text'] = previous_item.text + ' ' + item.text
        
        return entities

    def is_multitag_item(self, item, previous_item):
        return item.tag.split('-')[0] == 'I' and previous_item.tag.split('-')[1] == item.tag.split('-')[1]


    '''
    Calculate position and create NamedEntity instances
    '''
    def convert(self, stanford_entities):
        named_entities = []
        
        offset = 0
        for se in stanford_entities:
            text = se["text"]
            pos = self.text_input[offset:].find(text)
            position = pos + offset
            offset += pos + len(text)
            
            ne = NamedEntity(text, "stanford", position, se['type'])
            named_entities.append(ne)
        
        return named_entities


    def translate(self, stanford_type):
        if stanford_type == "I-PER" or stanford_type == "B-PER":
            return "PERSON"
        if stanford_type == "I-LOC" or stanford_type == "B-LOC":
            return "LOCATION"


    def join(self):
        threading.Thread.join(self)
        return self.result
    