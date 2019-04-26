from .spacy import Spacy

from multiNER.named_entity_kit import NamedEntity

def test_parse_response(): 
    s = get_instance()

    fake_entity1 = MockSpacyEntity('Utrecht', 'LOCATION', 0)
    fake_entity2 = MockSpacyEntity('Gouda', 'LOCATION', 11)
    fake_entities = [fake_entity1, fake_entity2]
    fake_response = MockSpacyResponse(fake_entities)

    expected_ne1 = NamedEntity('Utrecht', 'spacy', 0, 'LOCATION')
    expected_ne2 = NamedEntity('Gouda', 'spacy', 11, 'LOCATION')

    assert s.parse_response(fake_response) == [expected_ne1, expected_ne2]


class MockSpacyResponse:
    def __init__(self, entities):
        self.ents = entities


class MockSpacyEntity:
    '''
    Note that the real spacy entities also have end_char available
    '''
    def __init__(self, text, label_, start_char):
        self.text = text
        self.label_ = label_
        self.start_char = start_char
        

def get_instance():
    return Spacy('nl', 'fake')