import logging

from curami.web import neo4j_connector, helper_service


def get_curations(page, size, user):
    logging.info("Get curations page={}, size={}, user={}", page, size, user)
    curations = neo4j_connector.get_suggested_curations(page, size, user)
    return curations


def save_curation(curation, user):
    logging.info("Save curation user={}, curation={}", user, curation)
    attribute_1 = curation['attribute_1']['name']
    attribute_2 = curation['attribute_2']['name']
    attribute_curated = curation['attribute_curated']

    if curation['type'] == 'SAME_AS':
        neo4j_connector.add_curation(attribute_1, attribute_2, attribute_curated, user)
    elif curation['type'] == 'DIFFERENT_FROM':
        neo4j_connector.reject_curation(attribute_1, attribute_2, user)
    elif curation['type'] == 'DIFFICULT_TO_SAY1':
        neo4j_connector.ignore_curation(attribute_1, attribute_2, user)
    else:
        raise helper_service.InvalidMessage("Invalid curation type: " + curation['type'], 400)
