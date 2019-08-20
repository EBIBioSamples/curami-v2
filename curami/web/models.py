from enum import Enum


class CurationType(Enum):
    LOOKS_SIMILAR = 1
    SAME_AS = 2
    DIFFERENT_FROM = 3
    DIFFICULT_TO_SAY = 4


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


class Curation:
    def __init__(self, attribute_1, attribute_2):
        self.id = attribute_1 + attribute_2
        self.attribute_1 = Attribute(attribute_1)
        self.attribute_2 = Attribute(attribute_2)
        self.attribute_curated = None
        self.type = None
        self.description = None
        self.confidence = None
        self.owner = None


