
from flask import current_app

class NamedEntity:

    def __init__(self, text, source, position, type):
        self.text = text
        self.source = source
        self.position = position
        self.type = type

    def __eq__(self, other):
        if isinstance(other, NamedEntity):
            return self.text == other.text and self.position == other.position and self.type == other.type
        return False


class IntegratedNamedEntity():

    def __init__(self, named_entity):
        self.text = named_entity.text
        self.start = named_entity.position
        self.end = self.start + len(named_entity.text)
        self.sources_types = { named_entity.source: named_entity.type }


    def get_sources(self):
        return list(self.sources_types.keys())


    def get_type(self):
        # TODO: fix this by making it configurable
        #print(current_app.config.get('NER_TYPE_PREFERENCE'))
        types_counts = self.get_types_counts()
        return max(types_counts, key=lambda key: types_counts[key]) 


    def get_type_certainty(self):
        types_counts = self.get_types_counts()
        type = max(types_counts, key=lambda key: types_counts[key])
        return types_counts[type]

    
    def get_types_counts(self):
        '''
        Returns a dict with this entities' types as keys and
        the count of how many times a type was suggested as value.
        '''
        type_count = {}
        
        for source, type in self.sources_types.items():
            if type in type_count:
                type_count[type] = type_count[type] + 1
            else:
                type_count[type] = 1

        return type_count


    def get_count(self):
        return len(self.sources_types)


    def add(self, named_entity):
        self.sources_types[named_entity.source] = named_entity.type

    # TODO: context


    def is_equal_to(self, named_entity):
        if isinstance(named_entity, NamedEntity):
            return self.start == named_entity.position
            
            #TODO: isn't this nicer? does it work for overlapping entities as described in #9?
            # if self.start <= named_entity.position <= self.end:
            #     return True
            # if named_entity.position <= self.start <= named_entity.position + len(named_entity.text):
            #     return True
        return False


def integrate(named_entities):
    integrated_nes = []
    
    for ne in named_entities:
        is_integrated = False
        
        for integrated_ne in integrated_nes:
            if integrated_ne.is_equal_to(ne):
                integrated_ne.add(ne)
                is_integrated = True
                break
        
        if not is_integrated:
            integrated_ne = IntegratedNamedEntity(ne)
            integrated_nes.append(integrated_ne)

    return integrated_nes
