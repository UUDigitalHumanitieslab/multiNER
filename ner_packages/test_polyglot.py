from .polyglot import Polyglot

from .named_entity import NamedEntity

def test_convert():
    p = get_instance()
    p.text_input = "Utrecht en Gouda"
    polyglot_entities = [{'text': 'Utrecht', 'type': 'LOCATION'}, {'text': 'Gouda', 'type': 'LOCATION'}]
    
    expected_ne1 = NamedEntity('Utrecht', 'polyglot', 0, 'LOCATION')
    expected_ne2 = NamedEntity('Gouda', 'polyglot', 11, 'LOCATION')
    
    assert p.convert(polyglot_entities) == [expected_ne1, expected_ne2]


def test_convert_test_position():
    p = get_instance()
    p.text_input = "Utrecht en Utrecht en utrecht en Utrecht"
    polyglot_entities = [{'text': 'Utrecht', 'type': 'LOCATION'}, 
                         {'text': 'Utrecht', 'type': 'LOCATION'},
                         {'text': 'utrecht', 'type': 'LOCATION'}]
    
    expected_ne1 = NamedEntity('Utrecht', 'polyglot', 0, 'LOCATION')
    expected_ne2 = NamedEntity('Utrecht', 'polyglot', 11, 'LOCATION')
    expected_ne3 = NamedEntity('utrecht', 'polyglot', 22, 'LOCATION')
    
    assert p.convert(polyglot_entities) == [expected_ne1, expected_ne2, expected_ne3]


def test_parse_response():
    p = get_instance()
    
    fake_entity1 = MockPolyglotEntity('Utrecht', 'I-LOC')
    fake_entity2 = MockPolyglotEntity('Gouda', 'I-LOC')
    
    fake_response = MockPolyGlotResponse([fake_entity1, fake_entity2])
    assert p.parse_response(fake_response) == [{'text': 'Utrecht', 'type': 'LOCATION'}, {'text': 'Gouda', 'type': 'LOCATION'}]


'''
The real Polyglot response looks like this (printed with print(vars(data))):
{'_BaseBlob__lang': None, 'hint_language_code': 'nl', 'raw': 'Utrecht en Gouda', 'string': 'Utrecht en Gouda'}
'''
class MockPolyGlotResponse:
    '''
    Note that the real Polyglot response also has a 'sentences' property that we are ignoring
    '''
    def __init__(self, entities):
        self.entities = entities

'''
The real Polyglot entities are a bit mysterious. print(vars(entity)) yields the following:
{'_collection': ['Utrecht'], 'parent': Text("Utrecht en Gouda"), 'end': 1, 'start': 0, 'tag': 'I-LOC'}

Both the code and this mock are based on this output.
'''
class MockPolyglotEntity:
    def __init__(self, text, tag):
        self._collection = []
        self._collection.append(text)
        self.tag = tag


def get_instance():
    return Polyglot('nl')