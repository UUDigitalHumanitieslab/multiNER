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
        self.start = named_entity.position
        self.end = self.start + len(named_entity.text)
        self.sources_types = {named_entity.source: named_entity.type}
        self.sources_texts = {named_entity.source: named_entity.text}
        self.alt_texts = []
        self.type_preferences = type_preferences
        self.right_context = ''
        self.left_context = ''

    def get_sources(self):
        '''
        Get a list of the ner packages that suggested this entity.
        '''
        return list(self.sources_types.keys())

    def was_suggested_by(self, source):
        '''
        Determine whether this named entity was suggested by a certain ner package.
        '''
        return source in self.get_sources()

    def get_text(self):
        '''
        Get the text representing this entity. If multiple strings were suggested for the same position(s),
        the following logic applies: if one is suggested most often, this one is chosen. If multiple texts 
        are suggested evenly (e.g. 'Jane' once and 'Jane Doe' once), the text is chosen based on type 
        preference. This implies that in more complicated scenarios, the text might be chosen based on which
        entity was inserted first. Consider the following suggestions: 
            [{'John':'PERSON}, {'John':'LOCATION'}, {'John Doe':'PERSON}, {'John Doe':'LOCATION}]
        Based on type preference the texts will either be 'John' or 'John Doe' and the outcome of alt_texts 
        the other one. This depends on chance, since there is no other sensible way to make a better choice. 
        '''
        texts_counts = self.get_value_count(self.sources_texts.items())
        texts_with_highest_count = self.get_keys_with_highest_count(
            texts_counts.items())

        if len(texts_with_highest_count) == 1:
            return texts_with_highest_count[0]
        else:
            for source, type in self.sources_types.items():
                if type == self.get_type():
                    return self.sources_texts[source]

    def get_alt_texts(self):
        '''
        Get the alternative texts for this entity. Follows the same logic as get_text(), but opposite.
        See the documentation there.
        '''
        self_text = self.get_text()
        alt_texts = []

        for source, text in self.sources_texts.items():
            if not text == self_text and text not in alt_texts:
                alt_texts.append(text)

        return alt_texts

    def get_type(self):
        '''
        Get the type of the entity. If multiple types are suggested, the one with the highest count is returned.
        If multiple types have equal count, type is chosen based on type preference.
        '''
        types_counts = self.get_value_count(self.sources_types.items())
        types_with_highest_counts = self.get_keys_with_highest_count(
            types_counts.items())

        if len(types_with_highest_counts) == 1:
            return types_with_highest_counts[0]
        else:
            return self.get_preferred_type(types_with_highest_counts)

    def get_keys_with_highest_count(self, dict_items):
        '''
        Helper method. Get the keys with the highest count in the form {key:count}.
        Might contain multiple entries (with the same count).
        '''
        max_count = 0
        keys_with_highest_value = []

        for key, count in dict_items:
            if count == max_count:
                keys_with_highest_value.append(key)
            elif count > max_count:
                keys_with_highest_value.clear()
                keys_with_highest_value.append(key)
                max_count = count

        return keys_with_highest_value

    def get_types(self):
        '''
        Get a list of all types suggested for this entity
        '''
        all_types = self.sources_types.values()
        unique_types = []
        for t in all_types:
            if not t in unique_types:
                unique_types.append(t)
        return unique_types

    def get_type_certainty(self):
        '''
        Get a representing the amount of ner packages that suggestde the type of this entity
        '''
        types_counts = self.get_value_count(self.sources_types.items())
        type = max(types_counts, key=lambda key: types_counts[key])
        return types_counts[type]

    def get_value_count(self, dict_items):
        '''
        Helper method. Returns a dict with the values of 'dict_items' as keys and
        the count of how many times each value was found as value.
        '''
        value_count = {}

        for key, value in dict_items:
            if value in value_count:
                value_count[value] = value_count[value] + 1
            else:
                value_count[value] = 1

        return value_count

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
        self.sources_texts[named_entity.source] = named_entity.text
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
            "ne": self.get_text(),
            "alt_nes": self.get_alt_texts(),
            "right_context": self.right_context,
            "left_context": self.left_context,
            "count": self.get_count(),
            "type": self.get_type(),
            "type_certainty": self.get_type_certainty(),
            "ner_src": self.get_sources(),
            "types": self.get_types()
        }



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


def filter_entities(integrated_named_entities, leading_packages, other_packages_min):
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
