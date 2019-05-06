from .named_entity_kit import *


def test_integrated_named_entity_get_type_certainty():
    ne = get_named_entities()[0]
    # create mock instance
    ine = IntegratedNamedEntity(ne, default_type_preferences())
    # replace source for type_certainty
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_type_certainty() == 2


def test_integrated_named_entity_get_type():
    ne = get_named_entities()[0]
    # create mock instance
    ine = IntegratedNamedEntity(ne, default_type_preferences)
    # replace source for type
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_type() == 'LOCATION'


def test_integrated_named_entity_get_types():
    ne = get_named_entities()[0]
    # create mock instance
    ine = IntegratedNamedEntity(ne, default_type_preferences)
    # replace source for type
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_types().sort() == ['LOCATION', 'OTHER'].sort()


def test_integrated_named_entity_get_count():
    ne = get_named_entities()[0]
    # create mock instance
    ine = IntegratedNamedEntity(ne, default_type_preferences)
    # replace source for count
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_count() == 3


def test_integrated_named_entity_get_sources():
    ne = get_named_entities()[0]
    # create mock instance
    ine = IntegratedNamedEntity(ne, default_type_preferences())
    # replace source for sources
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_sources().sort() == [
        'spacy', 'stanford', 'spotlight'].sort()


def test_integrated_named_entity_alt_text():
    entities = [
        NamedEntity('Utrecht University', 'stanford', 10, 'ORGANIZATION'),
        NamedEntity('Utrecht', 'polyglot', 10, 'LOCATION')
    ]
    
    ines = integrate(entities, {1: 'LOCATION', 2: 'ORGANIZATION'})
    assert len(ines) == 1
    
    ine = ines[0]
    assert ine.text == 'Utrecht'
    assert ine.alt_texts == ['Utrecht University']
    assert ine.get_type() == 'LOCATION'
    

def test_integrated_named_entity_alt_text_different_start():
    entities = [
        NamedEntity('Universiteit Utrecht', 'stanford', 10, 'ORGANIZATION'),
        NamedEntity('Utrecht', 'polyglot', 24, 'LOCATION')]
        
    ines = integrate(entities, {1: 'LOCATION', 2: 'ORGANIZATION'})
    assert len(ines) == 1

    ine = ines[0]
    assert ine.text == 'Utrecht'
    assert ine.alt_texts == ['Universiteit Utrecht']
    assert ine.get_type() == 'LOCATION'


def test_integrated_named_entity_add():
    initial_entity = NamedEntity('Alex Hebing', 'stanford', 0, 'PERSON')    
    ine = IntegratedNamedEntity(initial_entity, default_type_preferences())

    next_ne = NamedEntity('Alex Hebing', 'spacy', 0, 'PERSON')
    ine.add(next_ne)

    assert len(ine.sources_types) == 2
    assert ine.get_types() == ['PERSON']
    assert ine.alt_texts == []

    # Now insert one with preferred type
    next_ne = NamedEntity('Alex', 'polyglot', 0, 'LOCATION')
    ine.add(next_ne)

    assert len(ine.sources_types) == 3
    assert ine.get_types().sort() == ['PERSON', 'LOCATION'].sort()
    assert ine.text == 'Alex'
    assert ine.alt_texts == ['Alex Hebing']

    # Now insert one with same text and type as first one
    next_ne = NamedEntity('Alex Hebing', 'spotlight', 0, 'PERSON')
    ine.add(next_ne)

    # The below proves the add logic is still messy, especially with regard to integrating the type.
    # Let it fail till a solution is found / implemented.
    # See the TODO in the add() method.
    assert len(ine.sources_types) == 4
    assert ine.get_types().sort() == ['PERSON', 'LOCATION'].sort()
    assert ine.text == 'Alex'
    assert ine.alt_texts == ['Alex Hebing']


def test_integrate():
    entities = get_named_entities()
    actual_ines = integrate(entities, default_type_preferences())

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
    ine = IntegratedNamedEntity(entities[0], default_type_preferences())
    # replace source for sources
    ine.sources_types = {'spotlight': 'LOCATION',
                         'stanford': 'LOCATION', 'spacy': 'OTHER'}
    assert ine.get_sources().sort() == [
        'spacy', 'stanford', 'spotlight'].sort()


def test_integrate_two_types():
    entities = [
        NamedEntity('John Smith', 'stanford', 15, 'PERSON'),
        NamedEntity('John Smith', 'polyglot', 15, 'OTHER')]
    actual_ines = integrate(entities, {1: 'PERSON', 2: 'OTHER'})

    assert len(actual_ines) == 1

    ine = actual_ines[0]
    assert ine.get_count() == 2
    assert ine.get_type() == 'PERSON'
    assert ine.get_type_certainty() == 1


def test_filter_leading_packages():
    named_entities = []

    leading_packages = ['stanford', 'spotlight']
    
    index = 1
    for p in leading_packages:
        named_entities.append(NamedEntity('Gouda', p, index * 11, 'LOCATION'))
        index += 1
    
    ines = integrate(named_entities, default_type_preferences())
    assert len(ines) == 2

    fines = filter(ines, leading_packages, 2)
    assert len(fines) == 2

    # add one that should be excluded
    otherne = NamedEntity('Gouda', 'OTHERNERPACKAGE', 1, 'LOCATION')
    named_entities.append(otherne)

    ines = integrate(named_entities, default_type_preferences())
    assert len(ines) == 3
    
    fines = filter(ines, leading_packages, 2)
    assert len(fines) == 2


def test_filter_other_packages_min():
    named_entities = []

    leading_packages = ['stanford', 'spotlight']

    # generate 3 equal entities from different non-leading packages
    for index in range(1,4):
        named_entities.append(NamedEntity('Gouda', 'OTHERNERPACKAGE_{}'.format(index), 11, 'LOCATION'))
    
    ines = integrate(named_entities, default_type_preferences())
    assert len(ines) == 1

    fines = filter(ines, leading_packages, 2) 
    assert len(fines) == 1

    #insert one that should be excluded
    otherne = NamedEntity('Gouda', 'YETOTHERNERPACKAGE', 1, 'LOCATION')
    named_entities.append(otherne)

    ines = integrate(named_entities, default_type_preferences())
    assert len(ines) == 2
    
    fines = filter(ines, leading_packages, 2)
    assert len(fines) == 1


def test_set_contexts():
    complete_text = "A sentence with some good context AN ENTITY around a named entity that will surely be found!"
    ne = NamedEntity('AN ENTITY', 'stanford', 34, 'PERSON')
    ine = IntegratedNamedEntity(ne, default_type_preferences())
    set_contexts([ine,], complete_text, 3)

    assert ine.left_context == 'some good context'
    assert ine.right_context == 'around a named'

    set_contexts([ine,], complete_text, 6)

    assert ine.left_context == 'A sentence with some good context'
    assert ine.right_context == 'around a named entity that will'



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

def default_type_preferences():
    return { 1: 'LOCATION', 2: 'PERSON', 3: 'ORGANIZATION', 4: 'OTHER' }
