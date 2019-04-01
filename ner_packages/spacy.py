#!/usr/bin/env python3
import threading
import spacy


'''
MISC PER ORG LOC
'''
class Spacy(threading.Thread):
    '''
        Wrapper for Spacy.

        https://spacy.io/

        >>> test = "Deze iets langere test bevat de naam Einstein."
        >>> p = Spacy(parsed_text=test)
        >>> p.start()
        >>> import time
        >>> time.sleep(0.1)
        >>> from pprint import pprint
        >>> pprint(p.join())
        {'spacy': [{'ne': 'Einstein', 'pos': 37, 'type': 'person'}]}
    '''    
    nlp_spacy = None

    def __init__(self, language='en', text_input=''):
        threading.Thread.__init__(self)        
        self.text_input = text_input
        self.set_language(language)


    def set_language(self, language):
        self.nlp_spacy = spacy.load(language)


    def run(self):
        result = []
        try:
            doc = self.nlp_spacy(self.text_input)

            for ent in doc.ents:
                result.append({"ne": ent.text, "type": ent.label_})

            offset = 0
            for i, ne in enumerate(result):
                ne = ne["ne"]
                pos = self.text_input[offset:].find(ne)
                result[i]["pos"] = pos + offset
                offset += pos + len(ne)
        except Exception as e:
            print(e)
            pass

        self.result = {"spacy": result}


    def join(self):
        threading.Thread.join(self)
        return self.result
    