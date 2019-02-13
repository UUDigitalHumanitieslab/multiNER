#!/usr/bin/env python3
from .base_ner_package import BaseNerPackage

class BaseExternalNerPackage(BaseNerPackage):

    def __init__(self, host, port, timeout, languages=['en'], text_input=''):
        self.host = host
        self.port = port
        self.timeout = timeout
        super().__init__(languages, text_input)
        
