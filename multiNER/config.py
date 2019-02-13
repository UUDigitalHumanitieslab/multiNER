# Will be used in web-service and doctest.
EXAMPLE_URL = "http://resolver.kb.nl/resolve?"
EXAMPLE_URL += "urn=ddd:010381561:mpeg21:a0049:ocr"

# Baseurl for Stanford standalone NER setup.
# https://nlp.stanford.edu/software/crf-faq.shtml#cc
# (Use inlineXML)
STANFORD_HOST = "localhost"
STANFORD_PORT = 9898

# Baseurl for Spotlight rest-service.
# https://github.com/dbpedia-spotlight/dbpedia-spotlight/
SPOTLIGHT_HOST = "localhost"
SPOTLIGHT_PORT = "9090"
SPOTLIGHT_PATH = "/rest/annotate/"

# Timeout for external NER's (stanford, spotlight)
TIMEOUT = 1000