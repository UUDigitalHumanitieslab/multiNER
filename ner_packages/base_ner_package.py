#!/usr/bin/env python3
from abc import ABC, abstractmethod
import threading

class BaseNerPackage(ABC):
    config = None
    result = {}
    text_input = ''

    def __init__(self, languages=['en'], text_input=''):
        self.input = text_input

    
    
