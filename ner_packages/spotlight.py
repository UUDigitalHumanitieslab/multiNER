#!/usr/bin/env python3
import threading
import requests

class Spotlight(threading.Thread):
    '''
        Wrapper for DBpedia-Spotlight.

        https://www.dbpedia-spotlight.org/
        >>> t = "Richard Nixon bakt een taart voor zichzelf."
        >>> p = Spotlight(parsed_text=t)
        >>> p.start()
        >>> import time
        >>> time.sleep(1)
        >>> from pprint import pprint
        >>> pprint(p.join())
        {'spotlight': [{'ne': 'Richard Nixon', 'pos': 0, 'type': 'other'}]}
    '''

    def __init__(self, url, timeout, language='en', text_input='', confidence='0.9'):
        threading.Thread.__init__(self)
        self.url = url
        self.timeout = timeout
        self.language = language
        self.text_input = text_input        
        self.confidence = confidence

    
    def parse_type(self, item):
        if "location" in item.get("@types").lower():
            return "LOCATION"
        else:
            return "OTHER"
        

    def run(self):
        self.result = {"spotlight": []}

        if self.text_input is None: return
        data = {'text': self.text_input, 'confidence': str(self.confidence)}
        
        header = {"Accept": "application/json"}

        done = False
        retry = 0
        max_retry = 10

        while not done and retry < max_retry:
            try:
                response = requests.get(self.url,
                                        params=data,
                                        headers=header,
                                        timeout=self.timeout)
                
                data = response.json()
                result = []

                if data and data.get('Resources'):
                    for item in data.get('Resources'):
                        self.parse_type(item)
                        ne = {}
                        ne["ne"] = item.get('@surfaceForm')
                        ne["pos"] = int(item.get('@offset'))
                        ne["type"] = self.parse_type(item)
                        result.append(ne)

                self.result = {"spotlight": result}
                done = True
            except Exception as e:
                print('spotlight error:')
                print(e)
                self.result = {"spotlight": []}
                retry += 1


    def join(self):
        threading.Thread.join(self)
        return self.result
