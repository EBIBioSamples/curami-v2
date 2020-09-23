import pandas as pd
from _datetime import datetime

from curami.commons import file_utils, mongo_connector


def generate_file():
    print('Generating curation rules csv file')
    curation_rules = []

    # Basic cleanup attributes
    attribute_cleanup_df = pd.read_csv(file_utils.unique_attributes_file_final_diff, encoding=file_utils.encoding)
    for index, row in attribute_cleanup_df.iterrows():
        for i, x in enumerate(row):
            if i != 0 and x != '' and x == x and x != row[0]:  # nan check x == x
                curation_rules.append([x, row[0]])

    # Identified misspellings
    # attribute_misspelling_df = pd.read_csv(file_utils.dictionary_matched_attribute_file, encoding=file_utils.encoding)
    # for index, row in attribute_misspelling_df.iterrows():
    #     curation_rules.append([row[1], row[0]])

    curation_rules_df = pd.DataFrame(curation_rules)
    curation_rules_df.to_csv(file_utils.curation_rules_file,
                             header=['ATTRIBUTE_PRE', 'ATTRIBUTE_POST'], index=False, encoding=file_utils.encoding)
    print("File generated. Writing to database")
    save_to_mongo(curation_rules)


def save_to_mongo(curation_rules):
    db_connector = mongo_connector.MongoConnector()
    client = db_connector.get_client()

    db = client.biosamples
    for rule in curation_rules:
        curation_rule = {'_id': rule[0],
                         '_class': 'uk.ac.ebi.biosamples.mongo.model.MongoCurationRule',
                         'attributePre': rule[0],
                         'attributePost': rule[1],
                         'created': datetime.utcnow()
                         }

        db.mongoCurationRule.replace_one({'_id': curation_rule['_id']}, curation_rule, upsert=True)


if __name__ == '__main__':
    generate_file()
