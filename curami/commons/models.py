from enum import Enum


class RelationshipType(Enum):
    LOOKS_SIMILAR = 1
    SAME_AS = 2
    DIFFERENT_FROM = 3
    IGNORES = 4
    COOCCURS_WITH = 5

    @staticmethod
    def get_curation_type_names():
        return [RelationshipType.SAME_AS.name,
                RelationshipType.DIFFERENT_FROM.name,
                RelationshipType.DIFFERENT_FROM.name]


class User():
    def __init__(self):
        self.username = ''
        self.password = ''


class Sample:
    def __init__(self):
        self.username = ''
        self.password = ''


class Attribute:
    def __init__(self, name):
        self.name = name
        self.count = ''
        self.quality = ''


class Value:
    def __init__(self):
        self.username = ''
        self.password = ''


class AttributeRelationship:
    def __init__(self, rel_type):
        self.rel_type = rel_type
        self.priority = 0
        self.confidence = 0
        self.owner = ''


class Curation:
    def __init__(self, attribute_1, attribute_2):
        self.id = attribute_1 + attribute_2
        self.attribute_1 = Attribute(attribute_1)
        self.attribute_2 = Attribute(attribute_2)
        self.attribute_curated = None
        self.attribute_difference = None
        self.type = None
        self.description = None
        self.confidence = None
        self.owner = None
        self.status = 0
