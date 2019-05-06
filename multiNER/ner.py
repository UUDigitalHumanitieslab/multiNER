#!/usr/bin/env python3
'''
MultiNER

MultiNER combines the output from four different
named-entity recognition packages into one answer.

https://github.com/KBNLresearch/MultiNER

Copyright 2013, 2019 Willem Jan Faber,
KB/National Library of the Netherlands.

To install most external dependencies using the following command:

    # python3 setup.py

For Stanford and Spotlight, see their own manuals on howto install those:

    https://nlp.stanford.edu/software/crf-faq.shtml#cc

    https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki/Run-from-a-JAR
    https://github.com/dbpedia-spotlight/dbpedia-spotlight/

Once installed (With wanted language models), run the webservices so MultiNER can contact those:

    $ cd /path/to/stanford-ner-2018-10-16
    $ java -mx400m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer \
           -outputFormat inlineXML -encoding "utf-8" \
           -loadClassifier dutch.crf.gz -port 9898

    $ cd /path/to/spotlight
    $ java --add-modules java.xml.bind -jar dbpedia-spotlight-1.0.0.jar \
                         nl http://localhost:9090/rest

    There is a small shell-script (run_external_ners.sh) available for this,
    modify it to your needs, if you change port's or want to use an external server,
    please keep them in sync with this file (STANFORD_HOST/PORT, SPOTLIGHT_HOST/PORT).

Language models spacy and polyglot:

    There is a big try catch block surrounding the invocation of polyglot,
    there is a good reason for that, I cannot seem to be able to force it to
    use a specific language, it will do a lang-detect and handle on that info.
    If the guessed language is not present, it will throw an exception.

    You can soft-link mutiple languages to other languages, to fool the software
    into using a wanted language, for example:

    $ cd ~/polyglot_data/ner2; mkdir af; ln -s ./nl/nl_ner.pkl.tar.bz2 ./af/af_ner.pkl.tar.bz2

    # apt-get install python-numpy libicu-dev
    $ pip install polyglot
    $ polyglot download embeddings2.nl

    $ python -m spacy download nl
    $ python -m spacy download de
    $ python -m spacy download fr
    $ python -m spacy download nl
    $ python -m spacy download en


Running test, and stable web-service:

    $ python3 ./ner.py

    This will run the doctest, if everything works, and external services are up,
    0 errors should be the result.

    $ gunicorn -w 10 web:application -b :8099

    Afther this the service can be envoked like this:

    $ curl -s localhost:8099/?url=http://resolver.kb.nl/resolve?urn=ddd:010381561:mpeg21:a0049:ocr

    If you expect to process a lot:

    # echo 1 > /proc/sys/ipv4/tcp_tw_recycle

    Else there will be no socket's left to process.
    
    
TODO:
hack this in somehow..:

from flask import abort, Flask, jsonify, request
from flair.models import SequenceTagger
from flair.data import Sentence
from segtok.segmenter import split_single

app = Flask(__name__)

tagger = SequenceTagger.load('ner-multi')

@app.route('/<text>', methods=['GET'])
def ner(text="Dit is een verhaal over dhr Willem Jan Faber."):
    global SequenceTagger
    sentences = [Sentence(sent, use_tokenizer=True) for sent in split_single(text)]
    tagger.predict(sentences)
    return jsonify([s.to_dict(tag_type='ner') for s in sentences])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8084)
'''


from ner_packages.stanford import Stanford
from ner_packages.spotlight import Spotlight
from ner_packages.spacy import Spacy
from ner_packages.polyglot import Polyglot

from .named_entity_kit import integrate, filter, set_contexts


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
                raise ImproperlyConfiguredException("Setting '{}' is required. Add it to your app_config.".format(rs))
         

    def find_entities(self, input):
        results = {}

        for part in input:
            text = input[part]
            entities = self.get_entities_from_ner_packages(text)
            integrated_entities = integrate(entities, self.configuration.type_preference)            
            filtered_ines = filter(integrated_entities, self.configuration.leading_packages, self.configuration.other_packages_min)
            set_contexts(filtered_ines, input[part], self.configuration.context_length)
                        
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
        parsers = { "polyglot": Polyglot,
                    "spacy": Spacy,
                    "spotlight": Spotlight 
                }

        if not self.configuration.language == 'it':
            parsers['stanford'] = Stanford

        return parsers


    def get_stanford_port(self):
        if self.configuration.language == 'nl':
            return self.app_config.get('STANFORD_NL_PORT')
        elif self.configuration.language == 'en':
            return self.app_config.get('STANFORD_EN_PORT')


    def get_spotlight_url(self):
        if self.configuration.language == 'nl':
            return self.app_config.get('SPOTLIGHT_NL_URL')
        elif self.configuration.language == 'en':
            return self.app_config.get('SPOTLIGHT_EN_URL')
        elif self.configuration.language == 'it':
            return self.app_config.get('SPOTLIGHT_IT_URL')

