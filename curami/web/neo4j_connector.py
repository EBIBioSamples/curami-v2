import sys
import logging

from py2neo import Graph, NodeMatcher, RelationshipMatcher, NodeMatch, RelationshipMatch, Node, Relationship
from neo4j import GraphDatabase

# sys.path.append("/home/isuru/Projects/curami-v2")

from curami.web.models import Curation

db_url = 'http://localhost:7474/db/data'
username='neo4j'
password='neo5j'


def get_attribute_relationships(page, size):
    relationships = []
    graph = connect_to_graph()

    rel_match = RelationshipMatch(graph, r_type='cooccurs_with', skip=page*size, limit=size).order_by("_.correlation")
    for relation in rel_match.__iter__():
        curation = Curation(relation.nodes[0]['attribute'], relation.nodes[1]['attribute'])
        relationships.append(curation)

    return relationships


def get_suggested_curations(page, size, user):
    curations = []
    graph = connect_to_graph()

    rel_match = RelationshipMatch(graph, r_type='LOOKS_SIMILAR', skip=(page-1)*size, limit=size).order_by("_.confidence")
    # rel_match = RelationshipMatch(graph, r_type='looks_similar', skip=page*size, limit=size).order_by("_.correlation")
    for relation in rel_match.__iter__():
        attribute_1 = relation.nodes[0]['name']
        attribute_2 = relation.nodes[1]['name']
        curation = Curation(attribute_1, attribute_2)

        print(attribute_1 + "_" + attribute_2 + "_" + user)
        type, attribute_curated = get_manual_curations(attribute_1, attribute_2, user)
        if type is not None:
            curation.attribute_curated = attribute_curated
            curation.type = type


        curations.append(curation)

    return curations


def get_manual_curations(attribute_1, attribute_2, user):
    relationships = []
    graph = connect_to_graph()

    results = graph.run("MATCH (a:Attribute {name: '" + attribute_1 + "'})-[r]->"
                        "(b:Attribute {name: '" + attribute_2 + "'}) WHERE r.owner='" + user + "'  RETURN r")

    for relation in results:
        if type(results['r']).__name__ != 'LOOKS_SIMILAR':
            return type(results['r']).__name__, relation['r']['attribute']

    return None, None
        # relationship = relation['r']
        # node_1 = relationship.start_node
        # node_2 = relationship.end_node
        # relationship['attribute']
        # relationship['owner']
        # type(results['r']).__name__
        # relationships.append((relation['r']))


def get_relationships(attribute_1, attribute_2):
    relationships = []
    # graph = GraphDatabase.driver(db_url, auth=(username, password))
    graph = connect_to_graph()

    results = graph.run("MATCH (:attribute {attribute: 'sample type'})-[r]-"
                        "(:attribute {attribute: 'vioscreen d total'}) RETURN r")
    for relation in results:
        relationships.append((relation['r']))

    return relationships


def get_relationships2(attribute_1, attribute_2):
    relationships = []
    graph = connect_to_graph()

    node_1 = Node("attribute", attribute=attribute_1)
    node_2 = Node("attribute", attribute=attribute_2)
    rel_match = RelationshipMatch(graph, nodes=[node_1, node_2])
    for relation in rel_match.__iter__():
        relationships.append(relation)

    return relationships


def add_curation(attribute_1, attribute_2, attribute_curated, user):
    graph = connect_to_graph()

    delete_created_relationships = "MATCH (a:Attribute {name: '" + attribute_1 + "'})-[r]->(b:Attribute {name: '" + attribute_2 + "'}) " \
                                   "WHERE (a)-[r:SAME_AS {owner : '" + user + "'}]-(b) " \
                                        "OR (a)-[r:DIFFERENT_FROM {owner : '" + user + "'}]-(b) " \
                                        "OR (a)-[r:DIFFICULT_TO_SAY {owner : '" + user + "'}]-(b) " \
                                   "DELETE r"

    create_relationship = "MATCH (a:Attribute),(b:Attribute) " \
                          "WHERE a.name = '" + attribute_1 + "' AND b.name = '" + attribute_2 + "' " \
                          "CREATE (a)-[r:SAME_AS {owner: '" + user + "', attribute: '" + attribute_curated + "'}]->(b) " \
                          "RETURN type(r)"
    graph.run(delete_created_relationships)
    graph.run(create_relationship)


def reject_curation(attribute_1, attribute_2, user):
    logging.info("Rejected")
    graph = connect_to_graph()

    delete_created_relationships = "MATCH (a:Attribute {name: '" + attribute_1 + "'})-[r]->(b:Attribute {name: '" + attribute_2 + "'}) " \
                                   "WHERE (a)-[r:SAME_AS {owner : '" + user + "'}]-(b) " \
                                          "OR (a)-[r:DIFFERENT_FROM {owner : '" + user + "'}]-(b) " \
                                          "OR (a)-[r:DIFFICULT_TO_SAY {owner : '" + user + "'}]-(b) " \
                                   "DELETE r"

    create_relationship = "MATCH (a:Attribute),(b:Attribute) " \
                          "WHERE a.name = '" + attribute_1 + "' AND b.name = '" + attribute_2 + "' " \
                          "CREATE (a)-[r:DIFFERENT_FROM {owner: '" + user + "'}]->(b) " \
                          "RETURN type(r)"
    graph.run(delete_created_relationships)
    graph.run(create_relationship)


def ignore_curation(attribute_1, attribute_2, user):
    logging.info("Ignored")
    graph = connect_to_graph()

    delete_created_relationships = "MATCH (a:Attribute {name: '" + attribute_1 + "'})-[r]->(b:Attribute {name: '" + attribute_2 + "'}) " \
                                   "WHERE (a)-[r:SAME_AS {owner : '" + user + "'}]-(b) " \
                                          "OR (a)-[r:DIFFERENT_FROM {owner : '" + user + "'}]-(b) " \
                                          "OR (a)-[r:DIFFICULT_TO_SAY {owner : '" + user + "'}]-(b) " \
                                   "DELETE r"

    create_relationship = "MATCH (a:Attribute),(b:Attribute) " \
                          "WHERE a.name = '" + attribute_1 + "' AND b.name = '" + attribute_2 + "' " \
                          "CREATE (a)-[r:DIFFICULT_TO_SAY {owner: '" + user + "'}]->(b) " \
                          "RETURN type(r)"

    graph.run(delete_created_relationships)
    graph.run(create_relationship)


# authentication
def create_user(username, password_hash):
    graph = connect_to_graph()
    userNode = Node("User", username=username, password=password_hash)
    graph.create(userNode)


def get_user(username):
    graph = connect_to_graph()
    node_matcher = NodeMatcher(graph)
    node = node_matcher.match('User', username=username).first()
    return node



def connect_to_graph():
    graph = Graph('http://localhost:7474/db/data', user='neo4j', password='neo5j')
    return graph


if __name__ == '__main__':
    # print(len(get_curations(0, 5)))
    # print(len(get_relationships2('sample type', 'vioscreen d total')))
    # create_user('isuru', 'isuru')
    # usernode = get_user('isuru')
    # print(usernode)
    relations = get_manual_curations('', '', '')
    print(relations)
