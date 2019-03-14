# Will be used in web-service and doctest.
EXAMPLE_URL = "http://resolver.kb.nl/resolve?"
EXAMPLE_URL += "urn=ddd:010381561:mpeg21:a0049:ocr"

# Baseurl for Stanford standalone NER setup.
# https://nlp.stanford.edu/software/crf-faq.shtml#cc
# Note that the multiNER class will open a Telnet connection,
# so make sure it has access / permissions 
# STANFORD_HOST = "dh.ner.hum.uu.nl"
# STANFORD_PORT = 9898
STANFORD_HOST = 'localhost'
STANFORD_PORT = '9898'

# Baseurl for Spotlight rest-service.
# https://github.com/dbpedia-spotlight/dbpedia-spotlight/
SPOTLIGHT_HOST = "localhost"
SPOTLIGHT_PORT = '2222'
SPOTLIGHT_PATH = "/rest/annotate/"


# SPOTLIGHT_HOST = "dh.ner.hum.uu.nl/dbpedia"
# SPOTLIGHT_PORT = None
# SPOTLIGHT_PATH = "/rest/annotate/"

# Timeout for external NER's (stanford, spotlight)
TIMEOUT = 1000

SECRET_KEY = 'topsecret'