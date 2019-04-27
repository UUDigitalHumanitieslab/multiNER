
from .config import NER_LEADING_PACKAGES, NER_OTHER_PACKAGES_MINIMUM, NER_TYPE_PREFERENCE

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
        types_counts = self.get_types_counts()

        max_count = 0
        suggested_types = []

        for type, count in types_counts.items():
            if count == max_count:
                suggested_types.append(type)
            elif count > max_count:
                suggested_types.clear()
                suggested_types.append(type)
                max_count = count

        return self.get_preferred_type(suggested_types) 


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

    
    def get_preferred_type(self, types):
        '''
        If multiple types are suggested (e.g. PERSON by spacy and OTHER by polyglot),
        pick one based on the preference defined in the config
        '''
        if len(types) == 1:
            return types[0]
        else:
            preferred_type = ''
            for index in range(1, len(NER_TYPE_PREFERENCE)):
                if NER_TYPE_PREFERENCE[index] in types:
                    preferred_type = NER_TYPE_PREFERENCE[index]
                    break
            return preferred_type


    def get_count(self):
        return len(self.sources_types)


    def add(self, named_entity):
        self.sources_types[named_entity.source] = named_entity.type

    
    def set_context(self, complete_text, context_len):
        '''
        Set the context of the current entity
        '''
        leftof = complete_text[:self.start].strip()
        l_context = " ".join(leftof.split()[-context_len:])

        rightof = complete_text[self.end:].strip()
        r_context = " ".join(rightof.split()[:context_len])
        
        self.left_context = l_context 
        self.right_context = r_context


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
