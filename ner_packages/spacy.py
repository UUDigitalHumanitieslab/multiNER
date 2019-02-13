#!/usr/bin/env python3
import threading
import spacy

# Preload Dutch data.
nlp_spacy = spacy.load('nl')

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

    def __init__(self, language='en', text_input=''):
        threading.Thread.__init__(self)
        self.language = language
        self.text_input = text_input

    def run(self):
        result = []
        try:
            doc = nlp_spacy(self.text_input)

            for ent in doc.ents:
                result.append({"ne": ent.text, "type": ent.label_})

            offset = 0
            for i, ne in enumerate(result):
                ne = ne["ne"]
                pos = self.text_input[offset:].find(ne)
                result[i]["pos"] = pos + offset
                offset += pos + len(ne)
        except Exception:
            pass

        self.result = {"spacy": result}


    def join(self):
        threading.Thread.join(self)
        return self.result
    