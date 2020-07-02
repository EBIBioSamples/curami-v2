import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm

from config_params import NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD
from curami.commons import common_utils, file_utils
from curami.commons.models import RelationshipType


# neo4j	1.7.4	4.0.0
# neobolt	1.7.4	1.7.17

class Neo4jConnector:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def get_suggested_curations(self, page, size, user):
        with self.driver.session() as session:
            results = session.run("MATCH(a:Attribute)-[r:LOOKS_SIMILAR]->(b:Attribute) RETURN COUNT(r) as total_count")
            for result in results:
                total_records = result["total_count"]

        with self.driver.session() as session:
            results = session.run("MATCH(a:Attribute)-[r:LOOKS_SIMILAR]->(b:Attribute) " +
                                  "RETURN r.owner as owner, r.score as score, r.class as class, TYPE(r) as type, " +
                                  "a.name as attribute_name, a.count as attribute_count, "
                                  "a.quality as attribute_quality, " +
                                  "b.name as curation_name, b.count as curation_count, b.quality as curation_quality " +
                                  "ORDER BY attribute_count DESC SKIP $skip LIMIT $limit", skip=page * size,
                                  limit=size)
            curation_records = self.collect_curation_records_from_db_result(results)

        aggregated_curation_records = []
        for curation_record in curation_records:
            attribute_names = [attribute["name"] for attribute in curation_record["attributes"]]
            manual_curation_records = self.get_manual_curations(attribute_names, user)
            aggregated_curation_record = curation_record
            for manual_curation_record in manual_curation_records:
                aggregated_curation_record = self.merge_curation_records(aggregated_curation_record,
                                                                         manual_curation_record)

            aggregated_curation_records.append(aggregated_curation_record)

        return {'total_records': total_records, 'page': page, 'size': size, 'records': aggregated_curation_records}

    def get_curation(self, attribute_name, curation_name, user):
        with self.driver.session() as session:
            results = session.run(
                "MATCH(a:Attribute {name: $attribute})-[r:LOOKS_SIMILAR]->(b:Attribute {name: $curation}) " +
                "RETURN r.owner as owner, r.score as score, r.class as class, TYPE(r) as type, " +
                "a.name as attribute_name, a.count as attribute_count, "
                "a.quality as attribute_quality, " +
                "b.name as curation_name, b.count as curation_count, b.quality as curation_quality",
                attribute=attribute_name,
                curation=curation_name)
            curation_records = self.collect_curation_records_from_db_result(results)

        aggregated_curation_records = []
        for curation_record in curation_records:
            attribute_names = [attribute["name"] for attribute in curation_record["attributes"]]
            manual_curation_records = self.get_manual_curations(attribute_names, user)
            aggregated_curation_record = curation_record
            for manual_curation_record in manual_curation_records:
                aggregated_curation_record = self.merge_curation_records(aggregated_curation_record,
                                                                         manual_curation_record)

            aggregated_curation_records.append(aggregated_curation_record)

        return aggregated_curation_records[0]

    def get_manual_curations(self, attribute_names, user):
        with self.driver.session() as session:
            results = session.run(
                "MATCH (a:Attribute)-[r]->(b:Attribute) WHERE a.name IN $attributes AND r.owner = $owner " +
                "RETURN a.name AS attribute_name, a.count as attribute_count, a.quality as attribute_quality, " +
                "b.name as curation_name, b.count as curation_count, b.quality as curation_quality, " +
                "r.owner AS owner, r.score as score, r.class as class, TYPE(r) as type",
                owner=user, attributes=attribute_names)
            curation_records = self.collect_curation_records_from_db_result(results)
        return curation_records

    def curate_record(self, curation_records, user):
        with self.driver.session() as session:
            machine_attribute_name = None
            machine_curation_name = None
            for curation in curation_records["curations"]:
                if curation["type"] == RelationshipType.LOOKS_SIMILAR.name:
                    machine_attribute_name = curation["attribute"]
                    machine_curation_name = curation["curation"]

            results = session.run(
                "MATCH (a:Attribute { name: $attribute })-[r:DIFFERENT_FROM {owner: $user}]->(b:Attribute { name: $curation }) " +
                "DELETE r", attribute=machine_attribute_name, curation=machine_curation_name, user=user)

            for curation in curation_records["curations"]:
                if curation["type"] == RelationshipType.SAME_AS.name:
                    if curation["curation"] != machine_attribute_name and curation["curation"] != machine_curation_name:
                        results = session.run("MERGE (a:Attribute { name: $curation})", curation=curation["curation"])
                    results = session.run(
                        "MATCH (a:Attribute { name: $attribute })-[r:SAME_AS {owner: $user}]->() " +
                        "DELETE r", attribute=curation["attribute"], user=user)
                    results = session.run(
                        "MATCH (a:Attribute { name: $attribute })-[r:SAME_AS {owner: $user}]-(b:Attribute { name: $curation }) " +
                        "DELETE r", attribute=curation["attribute"], curation=curation["curation"], user=user)
                    results = session.run(
                        "MATCH (a:Attribute),(b:Attribute) WHERE a.name = $attribute AND b.name = $curation " +
                        "CREATE (a)-[r:SAME_AS {class: 'HUMAN', owner: $user, score: $score}]->(b)",
                        attribute=curation["attribute"], curation=curation["curation"], user=user, score=0.8)
                elif curation["type"] == RelationshipType.DIFFERENT_FROM.name:
                    results = session.run(
                        "MATCH (a:Attribute { name: $attribute })-[r:SAME_AS {owner: $user}]-(b:Attribute { name: $curation }) " +
                        "DELETE r", attribute=curation["attribute"], curation=curation["curation"], user=user)
                    results = session.run(
                        "MATCH (a:Attribute),(b:Attribute) WHERE a.name = $attribute AND b.name = $curation " +
                        "MERGE (a)-[r:DIFFERENT_FROM {class: 'HUMAN', owner: $user, score: $score}]->(b)",
                        attribute=curation["attribute"], curation=curation["curation"], user=user, score=0.8)

        return self.get_curation(machine_attribute_name, machine_curation_name, user)

    @staticmethod
    def collect_curation_records_from_db_result(results):
        curation_records = []
        for result in results:
            curation_record = {"attributes": [], "curations": []}
            curation_record["attributes"].append({"name": result["attribute_name"], "count": result["attribute_count"],
                                                  "quality": result["attribute_quality"]})
            curation_record["attributes"].append({"name": result["curation_name"], "count": result["curation_count"],
                                                  "quality": result["curation_quality"]})
            curation_record["curations"].append(
                {"attribute": result["attribute_name"], "curation": result["curation_name"], "type": result["type"],
                 "owner": result["owner"], "score": result["score"], "class": result["class"]})
            curation_records.append(curation_record)

        return curation_records

    @staticmethod
    def merge_curation_records(curation_records_1, curation_records_2):
        attributes = list(curation_records_1["attributes"])
        attributes.extend([x for x in curation_records_2["attributes"] if x not in curation_records_1["attributes"]])
        curations = list(curation_records_1["curations"])
        curations.extend([x for x in curation_records_2["curations"] if x not in curation_records_1["curations"]])

        return {"attributes": attributes, "curations": curations}

    def build_curation_graph(self):
        attribute_misspelling_df = pd.read_csv(file_utils.dictionary_matched_attribute_file,
                                               encoding=file_utils.encoding)
        print("Loading " + str(len(attribute_misspelling_df)) + " attribute relationships...")
        attribute_map = common_utils.build_attribute_map()
        with self.driver.session() as session:
            results = session.run("MATCH (n) DETACH DELETE n")

        with self.driver.session() as session:
            progress_bar = tqdm(total=len(attribute_misspelling_df), position=0, leave=True)
            for index, row in tqdm(attribute_misspelling_df.iterrows()):
                curation_name = row[0]
                attribute_name = row[1]
                results = session.run("MERGE (a:Attribute { name: $attribute, count: $count, quality: $quality })",
                                      attribute=curation_name, count=attribute_map[curation_name], quality=0)
                results = session.run("MERGE (a:Attribute { name: $attribute, count: $count, quality: $quality })",
                                      attribute=attribute_name, count=attribute_map[attribute_name], quality=0)
                results = session.run(
                    "MATCH (a:Attribute),(b:Attribute) WHERE a.name = $attribute AND b.name = $curation " +
                    "CREATE (a)-[r:LOOKS_SIMILAR {class: 'MACHINE', owner: 'dictionary', score: $score}]->(b)",
                    attribute=attribute_name, curation=curation_name, score=0.2)

                progress_bar.update(1)

        print("Finished loading data into neo4j")

    def get_user(self, username):
        user_password = ''
        with self.driver.session() as session:
            results = session.run("MATCH (a:User { username: $username }) RETURN a.password", username=username)
            user_password = results.single()["a.password"]
        return user_password

    # authentication
    def create_user(self, username, password_hash):
        with self.driver.session() as session:
            results = session.run("CREATE (a:User{ username: $username, password: $password }) RETURN a",
                                  username=username, password=password_hash)

        return results.single()


if __name__ == '__main__':
    connector = Neo4jConnector()
    connector.build_curation_graph()
    # curation_records = connector.get_suggested_curations(1, 10, 'Isuru')
    # print(len(curation_records))

    curation_record = {
        "attributes": [],
        "curations": [{
            "attribute": 'library contruction protocol',
            "curation": 'library construction protocol',
            "type": 'LOOKS_SIMILAR',
            "class": 'MACHINE',
            "owner": 'dictionary',
            "score": 0.8
        }, {
            "attribute": 'library contruction protocol',
            "curation": 'library contruction bitch protocol',
            "type": 'DIFFERENT_FROM',
            "class": 'HUMAN',
            "owner": 'Isuru',
            "score": 0.8
        }
            , {
                "attribute": 'library construction protocol',
                "curation": 'library contruction bitch protocol',
                "type": 'DIFFERENT_FROM',
                "class": 'HUMAN',
                "owner": 'Isuru',
                "score": 0.8
            }
            , {
                "attribute": 'library contruction protocol',
                "curation": 'library construction protocol',
                "type": 'DIFFERENT_FROM',
                "class": 'HUMAN',
                "owner": 'Isuru',
                "score": 0.8
            }
        ]
    }
    connector.curate_record(curation_record, 'isuru')
#
