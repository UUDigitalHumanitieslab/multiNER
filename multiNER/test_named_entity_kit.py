from .named_entity_kit import *


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
    # TODO: fix! This one fails half the time (i.e. fix the code)
    
    entities = [
        NamedEntity('John Smith', 'stanford', 15, 'PERSON'),
        NamedEntity('John Smith', 'polyglot', 15, 'OTHER')]
    actual_ines = integrate(entities)

    assert len(actual_ines) == 1
    
    for ine in actual_ines:
        if (ine.text == 'John Smith'):
            assert ine.get_count() == 2
            assert ine.get_type() == 'PERSON'
            assert ine.get_type_certainty() == 1

    # create mock instance
    ine = IntegratedNamedEntity(entities[0])
    # replace source for sources
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_sources().sort() == [
        'spacy', 'stanford', 'spotlight'].sort()


def get_named_entities():
    return [
        NamedEntity('Gouda', 'stanford', 11, 'LOCATION'),
        NamedEntity('Gouda', 'spotlight', 11, 'LOCATION'),
        NamedEntity('Gouda', 'spacy', 11, 'LOCATION'),
        NamedEntity('Gouda', 'polyglot', 11, 'LOCATION'),
        NamedEntity('Utrecht', 'polyglot', 0, 'OTHER'),
        NamedEntity('Utrecht', 'spacy', 0, 'LOCATION'),
        NamedEntity('Utrecht', 'stanford', 0, 'LOCATION'),
        NamedEntity('John Smith', 'spacy', 15, 'PERSON'),
        NamedEntity('John Smith', 'stanford', 15, 'PERSON'),
        NamedEntity('John Smith', 'polyglot', 15, 'OTHER')
    ]
