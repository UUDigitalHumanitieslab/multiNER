from .spotlight import Spotlight

from .named_entity import NamedEntity


def test_parse_response():
    s = get_instance()
    fake_response = {
        '@text': 'Utrecht en Gouda', 
        '@types': '', 
        '@confidence': '0.9', 
        '@sparql': '', 
        '@policy': 'whitelist', 
        '@support': '0', 
        'Resources': [{
            '@URI': 'http://nl.dbpedia.org/resource/Gouda', 
            '@percentageOfSecondRank': '0.007148695746376943', 
            '@types': 'Wikidata:Q3455524,Schema:Place,Schema:AdministrativeArea,DBpedia:Region,DBpedia:PopulatedPlace,DBpedia:Place,DBpedia:Municipality,DBpedia:Location,DBpedia:GovernmentalAdministrativeRegion,DBpedia:AdministrativeRegion', 
            '@offset': '11', 
            '@similarityScore': '0.9928671570101985', 
            '@support': '4825', 
            '@surfaceForm': 'Gouda'
            }]
        }

    expected_ne1 = NamedEntity('Gouda', "spotlight", 11, "LOCATION")

    assert s.parse_response(fake_response) == [expected_ne1,]


def test_parse_type():
    s = get_instance()
    spotlight_types = {'@types': 'Wikidata:Q3455524,Schema:Place,DBpedia:PopulatedPlace,DBpedia:Place,DBpedia:Location,DBpedia:AdministrativeRegion'}
    assert s.parse_type(spotlight_types) == "LOCATION"


'''
Note that currently only on the presence of the string 'location' the entity is considered a LOCATION.
'DBpedia:Place', for instance, is considered OTHER.
'''
def test_parse_type_place():
    s = get_instance()
    spotlight_types = {'@types': 'Wikidata:Q3455524,Schema:Place,DBpedia:PopulatedPlace,DBpedia:Place,DBpedia:AdministrativeRegion'}
    assert s.parse_type(spotlight_types) == "OTHER"


def get_instance():
    return Spotlight('bogus', 'blah', 'fake')

