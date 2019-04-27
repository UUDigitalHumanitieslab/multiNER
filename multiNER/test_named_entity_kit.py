from .named_entity_kit import *

from .config import *


def test_integrated_named_entity_get_type_certainty():
    ne = get_named_entities()[0]
    # create mock instance
    ine = IntegratedNamedEntity(ne)
    # replace source for type_certainty
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_type_certainty() == 2


def test_integrated_named_entity_get_type():
    ne = get_named_entities()[0]
    # create mock instance
    ine = IntegratedNamedEntity(ne)
    # replace source for type
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_type() == 'LOCATION'


def test_integrated_named_entity_get_count():
    ne = get_named_entities()[0]
    # create mock instance
    ine = IntegratedNamedEntity(ne)
    # replace source for count
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_count() == 3


def test_integrated_named_entity_get_sources():
    ne = get_named_entities()[0]
    # create mock instance
    ine = IntegratedNamedEntity(ne)
    # replace source for sources
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_sources().sort() == [
        'spacy', 'stanford', 'spotlight'].sort()


def test_integrated_named_entity_context():
    complete_text = "A sentence with some good context AN ENTITY around a named entity that will surely be found!"
    ne = NamedEntity('AN ENTITY', 'stanford', 34, 'PERSON')
    ine = IntegratedNamedEntity(ne)
    ine.set_context(complete_text, 3)

    assert ine.left_context == 'some good context'
    assert ine.right_context == 'around a named'

    ine.set_context(complete_text, 6)

    assert ine.left_context == 'A sentence with some good context'
    assert ine.right_context == 'around a named entity that will'


def test_integrated_named_entity_alt_text():
    entities = [
        NamedEntity('Utrecht University', 'stanford', 10, 'ORGANIZATION'),
        NamedEntity('Utrecht', 'polyglot', 10, 'LOCATION')
    ]
    
    ines = integrate(entities)
    assert len(ines) == 1

    expected_type = get_preferred_type(['LOCATION', 'ORGANIZATION'])
    expected_text = [ne for ne in entities if ne.type == expected_type][0].text
    expected_alt_text = [ne for ne in entities if not ne.type == expected_type][0].text

    ine = ines[0]
    assert ine.text == expected_text
    assert ine.alt_texts == [expected_alt_text]
    assert ine.get_type() == expected_type    
    

def test_integrated_named_entity_alt_text_different_start():
    entities = [
        NamedEntity('Universiteit Utrecht', 'stanford', 10, 'ORGANIZATION'),
        NamedEntity('Utrecht', 'polyglot', 24, 'LOCATION')]
        
    ines = integrate(entities)
    assert len(ines) == 1

    expected_type = get_preferred_type(['LOCATION', 'ORGANIZATION'])
    expected_text = [ne for ne in entities if ne.type == expected_type][0].text
    expected_alt_text = [ne for ne in entities if not ne.type == expected_type][0].text

    ine = ines[0]
    assert ine.text == expected_text
    assert ine.alt_texts == [expected_alt_text]
    assert ine.get_type() == expected_type


def test_integrate():
    entities = get_named_entities()
    actual_ines = integrate(entities)

    assert len(actual_ines) == 3

    for ine in actual_ines:
        if (ine.text == 'Utrecht'):
            assert ine.get_count() == 3
            assert ine.get_type() == 'LOCATION'
            assert ine.get_type_certainty() == 2
        if (ine.text == 'Gouda'):
            assert ine.get_count() == 4
            assert ine.get_type() == 'LOCATION'
            assert ine.get_type_certainty() == 4
        if (ine.text == 'John Smith'):
            assert ine.get_count() == 3
            assert ine.get_type() == 'PERSON'
            assert ine.get_type_certainty() == 2

    # create mock instance
    ine = IntegratedNamedEntity(entities[0])
    # replace source for sources
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_sources().sort() == [
        'spacy', 'stanford', 'spotlight'].sort()


def test_integrate_two_types():
    entities = [
        NamedEntity('John Smith', 'stanford', 15, 'PERSON'),
        NamedEntity('John Smith', 'polyglot', 15, 'OTHER')]
    actual_ines = integrate(entities)

    expected_type = get_preferred_type(['PERSON', 'OTHER'])

    assert len(actual_ines) == 1

    for ine in actual_ines:
        if (ine.text == 'John Smith'):
            assert ine.get_count() == 2
            assert ine.get_type() == expected_type
            assert ine.get_type_certainty() == 1


def test_filter_leading_packages():
    named_entities = []
    
    index = 1
    for p in NER_LEADING_PACKAGES:
        named_entities.append(NamedEntity('Gouda', p, index * 11, 'LOCATION'))
        index += 1
    
    ines = integrate(named_entities)
    assert len(ines) == len(NER_LEADING_PACKAGES)

    fines = filter(ines)
    assert len(fines) == len(NER_LEADING_PACKAGES)

    # add one that should be excluded
    otherne = NamedEntity('Gouda', 'OTHERNERPACKAGE', 1, 'LOCATION')
    named_entities.append(otherne)

    ines2 = integrate(named_entities)
    assert len(ines2) == len(NER_LEADING_PACKAGES) + 1
    
    fines = filter(ines2)
    assert len(fines) == len(NER_LEADING_PACKAGES)


def test_filter_other_packages_min():
    named_entities = []

    for index in range(1,4):
        named_entities.append(NamedEntity('Gouda', 'OTHERNERPACKAGE_{}'.format(index), 11, 'LOCATION'))
    
    ines = integrate(named_entities)
    assert len(ines) == 1

    fines = filter(ines) 
    assert len(fines) == 1

    #insert one that should be excluded
    otherne = NamedEntity('Gouda', 'YETOTHERNERPACKAGE', 1, 'LOCATION')
    named_entities.append(otherne)

    ines2 = integrate(named_entities)
    assert len(ines2) == 2
    
    fines = filter(ines2)
    assert len(fines) == 1


def get_named_entities():
    return [
        NamedEntity('Gouda', 'stanford', 11, 'LOCATION'),
        NamedEntity('Gouda', 'spotlight', 11, 'LOCATION'),
        NamedEntity('Gouda', 'spacy', 11, 'LOCATION'),
        NamedEntity('Gouda', 'polyglot', 11, 'LOCATION'),
        NamedEntity('Utrecht', 'polyglot', 0, 'OTHER'),
        NamedEntity('Utrecht', 'spacy', 0, 'LOCATION'),
        NamedEntity('Utrecht', 'stanford', 0, 'LOCATION'),
        NamedEntity('John Smith', 'spacy', 25, 'PERSON'),
        NamedEntity('John Smith', 'stanford', 25, 'PERSON'),
        NamedEntity('John Smith', 'polyglot', 25, 'OTHER')
    ]


def get_preferred_type(types):
    if len(types) == 1:
        return types[0]
    else:
        preferred_type = ''
        for index in range(1, len(NER_TYPE_PREFERENCE)):
            if NER_TYPE_PREFERENCE[index] in types:
                preferred_type = NER_TYPE_PREFERENCE[index]
                break
        return preferred_type
