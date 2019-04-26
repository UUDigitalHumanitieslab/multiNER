
class NamedEntity:

    def __init__(self, text, source, position, type):
        self.text = text
        self.source = source
        self.position = position
        self.type = type

    def __eq__(self, other):
        print(vars(other))
        if isinstance(other, NamedEntity):
            return self.text == other.text and self.position == other.position and self.type == other.type
        return False
