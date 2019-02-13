#!/usr/bin/env python3
import telnetlib
from lxml import etree
import threading

'''
PERSON ORGANIZATION LOCATION
'''
class Stanford(threading.Thread):
    '''
        Wrapper for Stanford.

        https://nlp.stanford.edu/software/CRF-NER.shtml

        >>> test = "Deze iets langere test bevat de naam Einstein."
        >>> p = Stanford(parsed_text=test)
        >>> p.start()
        >>> import time
        >>> time.sleep(0.1)
        >>> from pprint import pprint
        >>> pprint(p.join())
        {'stanford': [{'ne': 'Einstein', 'pos': 37, 'type': 'location'}]}
    '''

    def __init__(self, host, port, timeout, language='en', text_input=''):                
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.language = language
        self.timeout = timeout
        self.text_input = text_input
        

    def run(self):        
        self.result = {"stanford": []}

        text = self.text_input.replace('\n', ' ')

        done = False
        retry = 0
        max_retry = 10

        while not done and retry < max_retry:
            try:
                conn = telnetlib.Telnet(host=self.host,
                                        port=self.port,
                                        timeout=self.timeout)
                done = True
            except Exception as e:
                print(e)
                retry += 1

        if not done:
            self.result = {"stanford": []}
            return

        text = text.encode('utf-8') + b'\n'
        conn.write(text)
        raw_data = conn.read_all().decode('utf-8')        
        conn.close()

        data = etree.fromstring('<root>' + raw_data + '</root>')

        result = []

        p_tag = ''
        for item in data.iter():
            if not item.tag == 'root':
                if item.tag.split('-')[0] == 'I' and p_tag == item.tag.split('-')[1]:
                    result[-1]["ne"] = result[-1]["ne"] + ' ' + item.text
                else:
                    result.append({"ne": item.text,
                                   "type": item.tag})
                    p_tag = item.tag

                   

        offset = 0
        for i, ne in enumerate(result):
            ne = ne["ne"]
            pos = self.text_input[offset:].find(ne)
            result[i]["pos"] = pos + offset
            offset += pos + len(ne)

        self.result = {"stanford": result}


    def join(self):
        threading.Thread.join(self)
        return self.result
    