import logging

from curami.web import helper_service
from curami.commons import neo4j_connector
from curami.commons.models import RelationshipType, Attribute


def get_curations(page, size, user):
    logging.info("Get curations page=%d, size=%d, user=%s", page, size, user)
    curations = neo4j_connector.get_suggested_curations(page, size, user)
    return curations


def save_curation(curation, user):
    logging.info("Save curation user={}, curation={}", user, curation)
    attribute_1 = curation['attribute_1']['name']
    attribute_2 = curation['attribute_2']['name']
    attribute_curated = curation['attribute_curated']

    if RelationshipType.SAME_AS.name == curation['type']:
        neo4j_connector.add_curation(attribute_1, attribute_2, attribute_curated, user)

        if attribute_1 == attribute_curated:
            neo4j_connector.update_attribute_quality(attribute_1, 0.25)
            neo4j_connector.update_attribute_quality(attribute_2, -0.25)
        elif attribute_2 == attribute_curated:
            neo4j_connector.update_attribute_quality(attribute_1, -0.25)
            neo4j_connector.update_attribute_quality(attribute_2, 0.25)
        else:
            attribute = Attribute(attribute_curated)
            attribute.quality = 0.25
            neo4j_connector.create_attribute(attribute)
            neo4j_connector.add_curation(attribute_1, attribute_curated, attribute_curated, user)
            neo4j_connector.add_curation(attribute_2, attribute_curated, attribute_curated, user)

    elif RelationshipType.DIFFERENT_FROM.name == curation['type']:
        neo4j_connector.reject_curation(attribute_1, attribute_2, user)
    elif RelationshipType.IGNORES.name == curation['type']:
        neo4j_connector.ignore_curation(attribute_1, attribute_2, user)
    else:
        raise helper_service.InvalidMessage("Invalid curation type: " + curation['type'], 400)



# curation = {}
# curation['attribute_1'] = {}
# curation['attribute_2'] = {}
# curation['attribute_1']['name'] = 'time point of sample collection'
# curation['attribute_2']['name'] = 'timepoint of sample collection'
# curation['attribute_curated'] = "hello world"
# curation['type'] = RelationshipType.SAME_AS.name
#
# save_curation(curation, "isuru")
