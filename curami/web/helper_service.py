import logging


def get_attribute(attribute_name):
    logging.info('get next curation suggestion')


def get_samples(sample_accession):
    logging.info('get next curation suggestion')


def get_value(value_name):
    logging.info('get next curation suggestion')


def get_samples_from_attribute(attribute_name):
    logging.info('get next curation suggestion')


def get_values_from_attribute(attribute_name):
    logging.info('get next curations')


def get_attributes_from_samples(sample_accession):
    logging.info('save curation')


class InvalidMessage(Exception):
    status_code = 400

    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        message_dict = {}
        message_dict['message'] = self.message
        message_dict['status_code'] = self.status_code
        return message_dict
