#!/usr/bin/env python3
import ast
import threading
from polyglot.text import Text

'''
PER ORG LOC
'''
class Polyglot(threading.Thread):
    '''
        Wrapper for Polyglot.

        http://polyglot.readthedocs.io/en/latest/index.html

        >>> test = "Deze iets langere test bevat de naam Einstein."
        >>> p = Polyglot(parsed_text=test)
        >>> p.start()
        >>> import time
        >>> time.sleep(0.1)
        >>> from pprint import pprint
        >>> pprint(p.join())
        {'polyglot': [{'ne': 'Einstein', 'pos': 37, 'type': 'person'}]}
    '''

    def __init__(self, language='en', text_input=''):
        threading.Thread.__init__(self)
        self.language = language
        self.text_input = text_input


    def run(self):
        buffer_all = []

        try:
            text = Text(self.text_input, hint_language_code=self.language)

            for sent in text.sentences:
                entity_buffer = []
                prev_entity_start = -1
                for entity in sent.entities:
                    if entity not in entity_buffer:
                        # For some reason polyglot double's it's output.
                        if not prev_entity_start == entity.start:
                            prev_entity_start = entity.start
                            entity_buffer.append(entity)
                        else:
                            entity_buffer.pop()
                            entity_buffer.append(entity)

                for item in entity_buffer:
                    buffer_all.append(item)

            result = []
            for entity in buffer_all:
                # For there is no sane way to do this.
                ne = " ".join(ast.literal_eval(entity.__str__()))
                tag = str(entity.tag.split('-')[1])
                result.append({"ne": ne,
                               "type": tag})

            offset = 0
            for i, ne in enumerate(result):
                ne = ne["ne"]
                pos = self.text_input[offset:].find(ne)
                result[i]["pos"] = pos + offset
                offset += pos + len(ne)
        except Exception as e:
            print('polyglot error:')
            print(e)
            result = []

        self.result = {"polyglot": result}


    def join(self):
        threading.Thread.join(self)
        return self.result
