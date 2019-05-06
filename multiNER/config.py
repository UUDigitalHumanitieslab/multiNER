# Will be used in web-service and doctest.
EXAMPLE_URL = "http://resolver.kb.nl/resolve?"
EXAMPLE_URL += "urn=ddd:010381561:mpeg21:a0049:ocr"

# List of leading packages, i.e. the entities proposed by 
# these syatems will always be included, even if they are the
# only package that found it
NER_LEADING_PACKAGES = ['stanford', 'spotlight']

# If none of the NER packages from the LEADING_NER_PACKAGES setting
# have suggested an entity, require at least this number of packages
# propsing the entity before inclusion
NER_OTHER_PACKAGES_MINIMUM = 2


# Sometimes only two NER sustems might suggest a type, two different types.
# For example, stanford may say 'Utrecht' is a LOCATION, whereas polyglot suggests 'OTHER'.
# In this dict, specify the order of preference, i.e. which type should be picked in such a case.
# Note that the NER_LEADING_PACKAGES setting is ignored in such cases
NER_TYPE_PREFERENCE = { 1: 'LOCATION', 2: 'PERSON', 3: 'ORGANIZATION', 4: 'OTHER'}


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