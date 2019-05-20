from .stanford import Stanford
from lxml import etree

from multiNER.named_entity_kit import NamedEntity

def test_convert():
    s = get_instance()
    s.text_input = "Utrecht en Gouda"
    stanford_entities = [{'text': 'Utrecht', 'type': 'LOCATION'}, {'text': 'Gouda', 'type': 'LOCATION'}]
    
    expected_ne1 = NamedEntity('Utrecht', 'stanford', 0, 'LOCATION')
    expected_ne2 = NamedEntity('Gouda', 'stanford', 11, 'LOCATION')
    
    assert s.convert(stanford_entities) == [expected_ne1, expected_ne2]


def test_convert_test_position():
    s = get_instance()
    s.text_input = "Utrecht en Utrecht en utrecht en Utrecht"
    stanford_entities = [{'text': 'Utrecht', 'type': 'LOCATION'}, 
                         {'text': 'Utrecht', 'type': 'LOCATION'},
                         {'text': 'utrecht', 'type': 'LOCATION'}]
    
    expected_ne1 = NamedEntity('Utrecht', 'stanford', 0, 'LOCATION')
    expected_ne2 = NamedEntity('Utrecht', 'stanford', 11, 'LOCATION')
    expected_ne3 = NamedEntity('utrecht', 'stanford', 22, 'LOCATION')
    
    assert s.convert(stanford_entities) == [expected_ne1, expected_ne2, expected_ne3]


def test_parse_response_single():
    s = get_instance()
    fake_response = '<B-LOC>Utrecht</B-LOC> en <B-LOC>Gouda</B-LOC>'
    assert s.parse_response(fake_response) == [{'text': 'Utrecht', 'type': 'LOCATION'}, {'text': 'Gouda', 'type': 'LOCATION'}]


def test_parse_response_double():
    s = get_instance()
    fake_response = '<B-LOC>Utrecht</B-LOC> en <B-PER>Persoon</B-PER><I-PER>met achternaam</I-PER>'
    assert s.parse_response(fake_response) == [{'text': 'Utrecht', 'type': 'LOCATION'}, {'text': 'Persoon met achternaam', 'type': 'PERSON'}]


def test_is_multitag_item_single():
    s = get_instance()

    previous_item = None
    fake_data = etree.fromstring('<root><B-LOC>A location</B-LOC><B-PER>A person</B-PER></root>')

    for item in fake_data.iter():
        if not item.tag == 'root':
            assert s.is_multitag_item(item, previous_item) == False
            previous_item = item


def test_is_multitag_item_double():
    s = get_instance()

    previous_item = None
    fake_data = etree.fromstring(
        '<root><B-LOC>part 1</B-LOC><I-LOC>part 2</I-LOC></root>')

    for item in fake_data.iter():
        if item.text == 'part 1':
            assert s.is_multitag_item(item, previous_item) == False
            previous_item = item
        if item.text == 'part 2':
            assert s.is_multitag_item(item, previous_item) == True


def get_instance():
    return Stanford('bogus', 'test', 'blah')
