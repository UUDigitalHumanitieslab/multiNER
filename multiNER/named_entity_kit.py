import json


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

    def __str__(self):
        return "{}, {}, {}, {}".format(self.text, self.type, self.position, self.source)


class IntegratedNamedEntity():

    def __init__(self, named_entity, type_preferences):
        self.text = named_entity.text
        self.start = named_entity.position
        self.end = self.start + len(named_entity.text)
        self.sources_types = {named_entity.source: named_entity.type}
        self.alt_texts = []
        self.type_preferences = type_preferences
        self.right_context = ''
        self.left_context = ''

    def get_sources(self):
        return list(self.sources_types.keys())

    def was_suggested_by(self, source):
        return source in self.get_sources()

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

    def get_types(self):
        all_types = self.sources_types.values()
        unique_types = []
        for t in all_types:
            if not t in unique_types:
                unique_types.append(t)
        return unique_types

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
            for index in range(1, len(self.type_preferences)):
                if self.type_preferences[index] in types:
                    preferred_type = self.type_preferences[index]
                    break
            return preferred_type


    def get_count(self):
        return len(self.sources_types)


    def add(self, named_entity):        
        # TODO: type does not reflect logic implemented below!
        
        if not self.text == named_entity.text:
            if self.get_preferred_type([self.get_type(), named_entity.type]) == named_entity.type:
                if not self.text in self.alt_texts:
                    self.alt_texts.append(self.text)
                self.text = named_entity.text
            else:
                self.alt_texts.append(named_entity.text)

        self.sources_types[named_entity.source] = named_entity.type


    def is_equal_to(self, named_entity):
        if isinstance(named_entity, NamedEntity):
            if self.start <= named_entity.position <= self.end:
                return True
            if named_entity.position <= self.start <= named_entity.position + len(named_entity.text):
                return True
        return False


    def to_jsonable(self):
        return {
            "pos": self.start,
            "ne": self.text,
            "alt_nes": self.alt_texts,
            "right_context": self.right_context,
            "left_context": self.left_context,
            "count": self.get_count(),
            "type": self.get_type(),
            "type_certainty": self.get_type_certainty(),
            "ner_src": self.get_sources(),
            "types": self.get_types()
        }

    def __str__(self):
        return self.to_jsonable()


def integrate(named_entities, type_preferences):
    integrated_nes = []

    for ne in named_entities:
        is_integrated = False

        for integrated_ne in integrated_nes:
            if integrated_ne.is_equal_to(ne):
                integrated_ne.add(ne)
                is_integrated = True
                break

        if not is_integrated:
            integrated_ne = IntegratedNamedEntity(ne, type_preferences)
            integrated_nes.append(integrated_ne)

    return integrated_nes


def filter(integrated_named_entities, leading_packages, other_packages_min):
    filtered_ines = []

    for ine in integrated_named_entities:

        was_added = False
        
        for p in leading_packages:
            if ine.was_suggested_by(p):
                filtered_ines.append(ine)
                was_added = True
                break

        if not was_added and len(ine.get_sources()) >= other_packages_min:
            filtered_ines.append(ine)

    return filtered_ines


def set_contexts(integrated_named_entities, complete_text, context_len):
    '''
    Set the context for integrated named entities
    '''
    for ine in integrated_named_entities:    
        leftof = complete_text[:ine.start].strip()
        l_context = " ".join(leftof.split()[-context_len:])

        rightof = complete_text[ine.end:].strip()
        r_context = " ".join(rightof.split()[:context_len])

        ine.left_context = l_context
        ine.right_context = r_context
