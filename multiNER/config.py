# Will be used in web-service and doctest.
EXAMPLE_URL = "http://resolver.kb.nl/resolve?"
EXAMPLE_URL += "urn=ddd:010381561:mpeg21:a0049:ocr"

# url for Stanford standalone NER setup.
# https://nlp.stanford.edu/software/crf-faq.shtml#cc
# Note that the multiNER class will open a Telnet connection,
# so make sure it has access / permissions 
#STANFORD_HOST = "dh.ner.hum.uu.nl"
STANFORD_HOST = 'localhost'
STANFORD_NL_PORT = '9898'
STANFORD_EN_PORT = '9899'


# urls for Spotlight rest-services.
# https://github.com/dbpedia-spotlight/dbpedia-spotlight/
SPOTLIGHT_NL_URL = 'http://dh.ner.hum.uu.nl/dbpedia/nl/rest/annotate/'
SPOTLIGHT_EN_URL = 'http://dh.ner.hum.uu.nl/dbpedia/en/rest/annotate/'
SPOTLIGHT_IT_URL = 'http://dh.ner.hum.uu.nl/dbpedia/it/rest/annotate/'

# Timeout for external NER's (stanford, spotlight)
TIMEOUT = 1000

SECRET_KEY = 'topsecret'