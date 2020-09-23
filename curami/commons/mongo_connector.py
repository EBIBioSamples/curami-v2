from enum import Enum

from pymongo import MongoClient

from curami.commons.config_params import DB_URL, DB_USERNAME, DB_PASSWORD


class MongoCollections(Enum):
    CURATION_LINK = 'mongoCurationLink'
    SAMPLE = 'mongoSample'


class MongoConnector:
    def __init__(self):
        self.client = MongoClient(DB_URL, username=DB_USERNAME, password=DB_PASSWORD,
                                  authSource='admin', authMechanism='SCRAM-SHA-1')
        self.db = self.client.biosamples

    def get_curation_records(self):
        curations = self.db[MongoCollections.CURATION_LINK.value].find()
        for curation in curations:
            yield curation

    def get_client(self):
        return self.client


if __name__ == '__main__':
    connector = MongoConnector()
    connector.get_curation_records()
