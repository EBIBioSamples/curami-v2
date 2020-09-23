import logging
from neo4j import GraphDatabase

from py2neo import Graph, NodeMatcher, RelationshipMatch, Node
import pandas as pd
from tqdm import tqdm

from curami.commons import common_utils, file_utils
from curami.commons.models import Curation, RelationshipType
from curami.commons.config_params import NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD

# db_url = 'bolt://neo4j:7687'
db_url = "bolt://localhost:7687"
# db_url = "bolt://scooby.ebi.ac.uk:7687"
userName = "neo4j"
password = "neo5j"


# Neo4j 4.0.3
# neo4j	1.7.4	4.0.0
# neobolt	1.7.4	1.7.17


class Neo4jConnector:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def get_user(self, username):
        user_password = ''
        with self.driver.session() as session:
            results = session.run("MATCH (a:User { username: $username }) RETURN a.password", username=username)
            user_password = results.single()["a.password"]
        return user_password

    def create_user(self, username, password_hash):
        with self.driver.session() as session:
            results = session.run("CREATE (a:User{ username: $username, password: $password }) RETURN a",
                                  username=username, password=password_hash)

        return results.single()

    def get_suggested_curations(self, search_term, page, size, user):
        search_query = (
                    "WHERE a.name = '" + search_term + "' OR b.name = '" + search_term + "' ") if search_term else ""

        with self.driver.session() as session:
            results = session.run("MATCH(a:Attribute)-[r:LOOKS_SIMILAR]->(b:Attribute) RETURN COUNT(r) as total_count")
            for result in results:
                total_records = result["total_count"]

            results = session.run("MATCH(a:Attribute)-[r:LOOKS_SIMILAR]->(b:Attribute) " + search_query +
                                  "UNWIND [a.count, b.count] AS count " +
                                  "RETURN r.owner as owner, r.score as score, r.class as class, TYPE(r) as type, " +
                                  "a.name as attribute_name, a.count as attribute_count, "
                                  "a.quality as attribute_quality, " +
                                  "b.name as curation_name, b.count as curation_count, "
                                  "b.quality as curation_quality, " +
                                  "min(count) as min_count " +
                                  "ORDER BY min_count DESC SKIP $skip LIMIT $limit", skip=(page - 1) * size,
                                  limit=size)

            curations = []
            for result in results:
                attribute_1 = result["attribute_name"]
                attribute_2 = result["curation_name"]
                curation = Curation(attribute_1, attribute_2)

                curation.attribute_1.count = result["attribute_count"]
                curation.attribute_1.quality = result["attribute_quality"]
                curation.attribute_2.count = result["curation_count"]
                curation.attribute_2.quality = result["curation_quality"]

                status, rel_type, attribute_curated = self.get_manual_curations(attribute_1, attribute_2, user)
                if status != 0:
                    curation.attribute_curated = attribute_curated
                    curation.type = rel_type
                    curation.status = status

                curations.append(curation)

        return curations

    def get_manual_curations(self, attribute_1, attribute_2, user):
        attribute_names = [attribute_1, attribute_2]
        with self.driver.session() as session:
            results = session.run(
                "MATCH (a:Attribute)-[r]->(b:Attribute) WHERE a.name in $attributes AND r.owner = $owner " +
                "RETURN a.name AS attribute_name, b.name as curation_name, r.owner AS owner, r.score as score, r.class as class, TYPE(r) as type",
                owner=user, attributes=attribute_names)

            curation_count = 0
            curated_name = ''
            status = 0  # 0: no curations, -1: conflicts,  1,2: curations
            rel_type = None
            for result in results:
                if result["type"] == RelationshipType.SAME_AS.name:
                    if curation_count == 0:
                        curated_name = result["curation_name"]
                        rel_type = result["type"]
                        curation_count += 1
                        if result["attribute_name"] in attribute_names and result["curation_name"] in attribute_names:
                            status = 1
                            # return result["type"], curated_name
                        else:
                            status = -1
                    elif curation_count == 1:
                        curation_count += 1
                        rel_type = result["type"]
                        if curated_name == result["curation_name"]:
                            status = 2
                            # return result["type"], curated_name
                        else:
                            status = -1
                    else:
                        logging.error("Invalid status in db: more than one outgoing SAME_AS relationship")
                elif result["type"] == RelationshipType.DIFFERENT_FROM.name:
                    if result["attribute_name"] in attribute_names and result["curation_name"] in attribute_names:
                        status = 1
                        rel_type = result["type"]
                        # return result["type"], curated_name

        return status, rel_type, curated_name

    def add_curation(self, attribute_1, attribute_2, attribute_curated, user):
        with self.driver.session() as session:
            # delete SAME_AS manual outgoing relationship for user for two attributes
            session.run(
                "MATCH (a:Attribute)-[r:SAME_AS]->(b:Attribute) WHERE a.name IN $attributes AND r.owner = $user " +
                "DELETE r", attributes=[attribute_1, attribute_2], user=user)
            session.run(
                "MATCH (a:Attribute)-[r:DIFFERENT_FROM]->(b:Attribute) WHERE a.name = $attribute_1 "
                "AND b.name = $attribute_2 AND r.owner = $user " +
                "DELETE r", attribute_1=attribute_1, attribute_2=attribute_2, user=user)

            # create new manual relationship
            if attribute_curated == attribute_1:
                session.run(
                    "MATCH (a:Attribute),(b:Attribute) WHERE a.name = $attribute AND b.name = $curation " +
                    "CREATE (a)-[r:SAME_AS {class: 'HUMAN', owner: $user, confidence: $score}]->(b)",
                    attribute=attribute_2, curation=attribute_curated, user=user, score=0.8)
                session.run("MATCH (a:Attribute {name: $attribute}) SET a.quality = a.quality + $score RETURN a",
                            attribute=attribute_1, score=0.25)
            elif attribute_curated == attribute_2:
                session.run(
                    "MATCH (a:Attribute),(b:Attribute) WHERE a.name = $attribute AND b.name = $curation " +
                    "CREATE (a)-[r:SAME_AS {class: 'HUMAN', owner: $user, confidence: $score}]->(b)",
                    attribute=attribute_1, curation=attribute_curated, user=user, score=0.8)
                session.run("MATCH (a:Attribute {name: $attribute}) SET a.quality = a.quality + $score RETURN a",
                            attribute=attribute_2, score=0.25)
            else:
                session.run("MERGE (a:Attribute {name: $curation}) " +
                            "ON CREATE SET a:Manual, a.quality = 1, a.count = 0 " +
                            "ON MATCH SET a.quality = a.quality + $score",
                            curation=attribute_curated, score=0.25)
                session.run(
                    "MATCH (a:Attribute),(b:Attribute) WHERE a.name = $attribute AND b.name = $curation " +
                    "CREATE (a)-[r:SAME_AS {class: 'HUMAN', owner: $user, confidence: $score}]->(b)",
                    attribute=attribute_1, curation=attribute_curated, user=user, score=0.8)
                session.run(
                    "MATCH (a:Attribute),(b:Attribute) WHERE a.name = $attribute AND b.name = $curation " +
                    "CREATE (a)-[r:SAME_AS {class: 'HUMAN', owner: $user, confidence: $score}]->(b)",
                    attribute=attribute_2, curation=attribute_curated, user=user, score=0.8)

    def reject_curation(self, attribute_1, attribute_2, user):
        with self.driver.session() as session:
            # delete any manual relationship between two attributes for the user
            session.run(
                "MATCH (a:Attribute)-[r]-(b:Attribute) WHERE a.name = $attribute_1 AND a.name = $attribute_2 "
                "AND r.owner = $user " +
                "DELETE r", attribute_1=attribute_1, attribute_2=attribute_2, user=user)

            # create relationship
            session.run(
                "MATCH (a:Attribute),(b:Attribute) " +
                "WHERE a.name = $attribute_1 AND b.name = $attribute_2 "
                "CREATE (a)-[r:DIFFERENT_FROM {class: 'HUMAN', owner: $owner, confidence: 1}]->(b)",
                attribute_1=attribute_1, attribute_2=attribute_2, owner=user)

    def get_manual_curations_all(self):
        with self.driver.session() as session:
            results = session.run("MATCH(a:Attribute)-[r:LOOKS_SIMILAR]->(b:Attribute) "
                                  "WHERE (a)-[:SAME_AS|:IGNORES|:DIFFERENT_FROM]-() "
                                  "OR (b)-[:SAME_AS|:IGNORES|:DIFFERENT_FROM]-() "
                                  "RETURN a.name AS attribute_name, b.name AS curation_name")

            curation_map = {}
            for result in results:
                attribute_1 = result["attribute_name"]
                attribute_2 = result["curation_name"]
                if attribute_2 not in curation_map:
                    curation_map[attribute_2] = {"attribute": attribute_2, "suggested": attribute_1}

            node_relationships = session.run("MATCH (a:Attribute {name: $attribute})-[r]->(b) "
                                             "RETURN TYPE(r) AS rel_type, r.owner AS owner, b.name as curation",
                                             attribute=attribute_2)
            for r in node_relationships:
                r_type = r["rel_type"]

                if r_type == RelationshipType.SAME_AS.name:
                    curation_map[attribute_2][r['owner']] = r['curation']
                # elif r_type == RelationshipType.LOOKS_SIMILAR.name:
                #     curation_map[attribute_2][r['owner']] = r['curation']

        # curation_map_filtered = {k: v for k, v in curation_map.items() if v}
        pd_curations = pd.DataFrame.from_dict(curation_map, orient="index")
        # pd_curations = pd_curations[(pd_curations['isuru'] == pd_curations['isuru'])][(pd_curations['fuqi'] == pd_curations['fuqi'])]
        pd_curations = pd_curations.dropna()
        return pd_curations

    def build_curation_graph(self, filename, delete):
        attribute_misspelling_df = pd.read_csv(filename, encoding=file_utils.encoding)
        print("Loading " + str(len(attribute_misspelling_df)) + " attribute relationships...")
        attribute_map = common_utils.build_attribute_map()
        if delete:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")

        with self.driver.session() as session:
            progress_bar = tqdm(total=len(attribute_misspelling_df), position=0, leave=True)
            for index, row in tqdm(attribute_misspelling_df.iterrows()):
                curation_name = row[0]
                attribute_name = row[1]
                session.run("MERGE (a:Attribute { name: $attribute, count: $count, quality: $quality })",
                                      attribute=curation_name, count=attribute_map[curation_name], quality=0)
                session.run("MERGE (a:Attribute { name: $attribute, count: $count, quality: $quality })",
                                      attribute=attribute_name, count=attribute_map[attribute_name], quality=0)
                session.run(
                    "MATCH (a:Attribute),(b:Attribute) WHERE a.name = $attribute AND b.name = $curation " +
                    "CREATE (a)-[r:LOOKS_SIMILAR {class: 'MACHINE', owner: 'dictionary', score: $score}]->(b)",
                    attribute=attribute_name, curation=curation_name, score=0.2)

                progress_bar.update(1)

        print("Finished loading data into neo4j")

    def build_cooccurance_graph(self, filename, delete):
        coexistence_df = pd.read_csv(filename, encoding=file_utils.encoding)
        print("Loading " + str(len(coexistence_df)) + " Links from coexistence file")
        attribute_map = common_utils.build_attribute_map()
        if delete:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")

        with self.driver.session() as session:
            progress_bar = tqdm(total=len(coexistence_df), position=0, leave=True)
            for index, row in tqdm(coexistence_df.iterrows()):
                attribute1 = row["ATTRIBUTE_1"]
                attribute2 = row["ATTRIBUTE_2"]
                correlation = row["COUNT"]
                session.run("MERGE (a:Attribute {name: $attribute}) " +
                            "ON CREATE SET count: $count, quality: $quality",
                            attribute=attribute1, count=attribute_map[attribute1], quality=0)
                session.run("MERGE (a:Attribute {name: $attribute}) " +
                            "ON CREATE SET count: $count, quality: $quality",
                            attribute=attribute2, count=attribute_map[attribute2], quality=0)
                session.run(
                    "MATCH (a:Attribute),(b:Attribute) WHERE a.name = $attribute1 AND b.name = $attribute2 " +
                    "CREATE (a)-[r:COOCCURS_WITH {class: 'MACHINE', owner: 'correlate', correlation: $correlation}]->(b)",
                    attribute1=attribute1, attribute2=attribute2, correlation=correlation)

                progress_bar.update(1)

        print("Finished loading data into neo4j")


def connect_to_graph():
    graph = Graph(db_url, user=userName, password=password)
    return graph


if __name__ == '__main__':
    neo4j_conn = Neo4jConnector()
    # relations = neo4j_conn.get_manual_curations_all()
    # print(relations)
    neo4j_conn.build_curation_graph(file_utils.dictionary_matched_attribute_file, True)
