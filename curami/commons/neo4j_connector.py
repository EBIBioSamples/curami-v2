from neo4j import GraphDatabase

from py2neo import Graph, NodeMatcher, RelationshipMatch, Node
import pandas as pd

from curami.commons.models import Curation, RelationshipType
from config_params import NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD

# db_url = 'bolt://neo4j:7687'
db_url = "bolt://localhost:7687"
# db_url = "bolt://scooby.ebi.ac.uk:7687"
userName = "neo4j"
password = "neo5j"


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

    def get_suggested_curations(self, page, size, user):
        with self.driver.session() as session:
            results = session.run("MATCH(a:Attribute)-[r:LOOKS_SIMILAR]->(b:Attribute) RETURN COUNT(r) as total_count")
            for result in results:
                total_records = result["total_count"]

        results = session.run("MATCH(a:Attribute)-[r:LOOKS_SIMILAR]->(b:Attribute) " +
                              "RETURN r.owner as owner, r.score as score, r.class as class, TYPE(r) as type, " +
                              "a.name as attribute_name, a.count as attribute_count, "
                              "a.quality as attribute_quality, " +
                              "b.name as curation_name, b.count as curation_count, b.quality as curation_quality " +
                              "ORDER BY attribute_count DESC SKIP $skip LIMIT $limit", skip=page * size,
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

            rel_type, attribute_curated = self.get_manual_curations(attribute_1, attribute_2, user)
            if rel_type is not None:
                curation.attribute_curated = attribute_curated
                curation.type = rel_type

            curations.append(curation)

        return curations

    def get_manual_curations(self, attribute_1, attribute_2, user):
        attribute_names = [attribute_1, attribute_2]
        with self.driver.session() as session:
            results = session.run(
                "MATCH (a:Attribute)-[r]->(b:Attribute) WHERE a.name in $attributes AND r.owner = $owner " +
                "RETURN a.name AS attribute_name, b.name as curation_name, r.owner AS owner, r.score as score, r.class as class, TYPE(r) as type",
                owner=user, attributes=attribute_names)

            curated_name_count = 0
            curated_name = ''
            for result in results:
                if result["type"] == RelationshipType.SAME_AS.name:
                    if curated_name_count == 0:
                        curated_name = result["curation_name"]
                        curated_name_count += 1
                        if curated_name == attribute_1 or curated_name == attribute_2:
                            return result["type"], curated_name
                    elif curated_name_count == 1 and curated_name == result["curation_name"]:
                        return result["type"], curated_name
                elif result["type"] == RelationshipType.DIFFERENT_FROM.name:
                    if result["attribute_name"] in attribute_names and result["curation_name"] in attribute_names:
                        return result["type"], curated_name

        return None, None

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
                session.run("MERGE (a:Attribute { name: $curation, quality: 1, count: 0})",
                                      curation=attribute_curated)
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


def connect_to_graph():
    graph = Graph(db_url, user=userName, password=password)
    return graph


if __name__ == '__main__':
    neo4j_conn = Neo4jConnector()
    relations = neo4j_conn.get_manual_curations_all()
    print(relations)

