#!/usr/bin/env python3
from ner_packages.stanford import Stanford
from ner_packages.spotlight import Spotlight
from ner_packages.spacy import Spacy
from ner_packages.polyglot import Polyglot

from .named_entity_kit import integrate, filter_entities, set_contexts


class Configuration:
    def __init__(
        self,
        language,
        context_length,
        leading_packages,
        other_packages_min,
        type_preference
    ):
        self.language = language
        self.context_length = context_length
        self.leading_packages = leading_packages
        self.other_packages_min = other_packages_min
        self.type_preference = type_preference


class ImproperlyConfiguredException(Exception):
    pass


class MultiNER:

    def __init__(self, app_config, ner_configuration):
        '''
        Create an instance of the MultiNER class. 

        Keyword arguments:
            app_config -- The config object of the Flask app
            ner_configuration -- An instance of the Configuration class
        '''
        if not ner_configuration.language in ['en', 'nl', 'it']:
            raise ValueError(
                "Language '{}' is not supported by multiNER".format(ner_configuration.language))

        self.validate_app_config(app_config)
        self.app_config = app_config

        self.configuration = ner_configuration

    def validate_app_config(self, app_config):
        required_settings = [
            'STANFORD_HOST', 'STANFORD_NL_PORT', 'STANFORD_EN_PORT', 'SPOTLIGHT_NL_URL', 'SPOTLIGHT_EN_URL', 'SPOTLIGHT_IT_URL', 'TIMEOUT'
        ]

        for rs in required_settings:
            if not app_config.get(rs, False):
                raise ImproperlyConfiguredException(
                    "Setting '{}' is required. Add it to your app_config.".format(rs))

    def find_entities(self, input):
        results = {}

        for part in input:
            text = input[part]
            entities = self.get_entities_from_ner_packages(text)
            integrated_entities = integrate(
                entities, self.configuration.type_preference)
            filtered_ines = filter_entities(
                integrated_entities, self.configuration.leading_packages, self.configuration.other_packages_min)
            set_contexts(
                filtered_ines, input[part], self.configuration.context_length)

            results[part] = {
                'entities': [ine.to_jsonable() for ine in filtered_ines],
                'text': input[part]
            }

        return (results)

    def get_entities_from_ner_packages(self, text):
        tasks = []

        parsers = self.get_parsers()

        for p in parsers:
            if (p == "stanford"):
                tasks.append(parsers[p](
                    self.app_config.get('STANFORD_HOST'),
                    self.get_stanford_port(),
                    self.app_config.get('TIMEOUT'),
                    text_input=text))
            elif (p == "spotlight"):
                tasks.append(parsers[p](
                    self.get_spotlight_url(),
                    self.app_config.get('TIMEOUT'),
                    text_input=text))
            else:
                tasks.append(parsers[p](
                    text_input=text, language=self.configuration.language))

            tasks[-1].start()

        entities = []

        for task in tasks:
            entities.extend(task.join())

        return entities

    def get_parsers(self):
        parsers = {
            "polyglot": Polyglot,
            "spacy": Spacy,
            "spotlight": Spotlight,
            "stanford": Stanford
        }

        return parsers

    def get_stanford_port(self):
        if self.configuration.language == 'nl':
            return self.app_config.get('STANFORD_NL_PORT')
        elif self.configuration.language == 'en':
            return self.app_config.get('STANFORD_EN_PORT')
        elif self.configuration.language == 'it':
            return self.app_config.get('STANFORD_IT_PORT')

    def get_spotlight_url(self):
        if self.configuration.language == 'nl':
            return self.app_config.get('SPOTLIGHT_NL_URL')
        elif self.configuration.language == 'en':
            return self.app_config.get('SPOTLIGHT_EN_URL')
        elif self.configuration.language == 'it':
            return self.app_config.get('SPOTLIGHT_IT_URL')
