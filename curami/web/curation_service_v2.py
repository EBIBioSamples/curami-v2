from curami.commons import neo4j_connector_v2 as neo4j_connector


class CurationService:
    def __init__(self):
        self.db_connection = neo4j_connector.Neo4jConnector()


def get_curations(page, size, user):
    # logging.info("Get curations page=%d, size=%d, user=%s", page, size, user)
    db_connection = neo4j_connector.Neo4jConnector()
    curations = db_connection.get_suggested_curations(page, size, user)
    return curations


def save_curation(curation, user):
    # logging.info("Save curation user={}, curation={}", user, curation)
    db_connection = neo4j_connector.Neo4jConnector()
    curations = db_connection.curate_record(curation, user)
    return curations
