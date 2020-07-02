import logging
import math

from py2neo import Graph, NodeMatcher, RelationshipMatch, Node
import pandas as pd

from curami.commons.models import Curation, RelationshipType

# db_url = 'bolt://neo4j:7687'
db_url = "bolt://localhost:7687"
# db_url = "bolt://scooby.ebi.ac.uk:7687"
userName = "neo4j"
password = "neo5j"


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
    results = graph.run("MATCH(a:Attribute)-[r:LOOKS_SIMILAR]->(b:Attribute) RETURN r "
                        "ORDER BY r.confidence DESC SKIP " + str((page-1)*size) + " LIMIT " + str(size))

    for relation in results:
        attribute_1 = relation['r'].start_node['name']
        attribute_2 = relation['r'].end_node['name']
        curation = Curation(attribute_1, attribute_2)

        curation.attribute_1.count = relation['r'].start_node['count']
        curation.attribute_1.quality = relation['r'].start_node['quality']
        curation.attribute_2.count = relation['r'].end_node['count']
        curation.attribute_2.quality = relation['r'].end_node['quality']

        rel_type, attribute_curated = get_manual_curations(attribute_1, attribute_2, user)
        if rel_type is not None:
            curation.attribute_curated = attribute_curated
            curation.type = rel_type

        curations.append(curation)

    return curations


def get_manual_curations_all():
    graph = connect_to_graph()
    results = graph.run("MATCH(a:Attribute)-[r:LOOKS_SIMILAR]->(b:Attribute) "
                        "WHERE (a)-[:SAME_AS|:IGNORES|:DIFFERENT_FROM]-() "
                        "OR (b)-[:SAME_AS|:IGNORES|:DIFFERENT_FROM]-() RETURN r")

    curation_map = {}

    for relation in results:
        attribute_1 = relation['r'].start_node['name']
        attribute_2 = relation['r'].end_node['name']
        if attribute_2 not in curation_map:
            curation_map[attribute_2] = {"attribute": attribute_2, "suggested": attribute_1}

        node_relationships = graph.run("MATCH (a:Attribute {name: '" + attribute_2 + "'})-[r]-(b) RETURN r")
        for r in node_relationships:
            r_type = type(r['r']).__name__

            if r_type == RelationshipType.SAME_AS.name:
                curation_map[attribute_2][r['r']['owner']] = r['r']['attribute']
            # elif r_type == RelationshipType.LOOKS_SIMILAR.name:
            #     curation_map[attribute_2][r['r']['owner']] = r['r']['attribute']


    # curation_map_filtered = {k: v for k, v in curation_map.items() if v}
    pd_curations = pd.DataFrame.from_dict(curation_map, orient="index")
    # pd_curations = pd_curations[(pd_curations['isuru'] == pd_curations['isuru'])][(pd_curations['fuqi'] == pd_curations['fuqi'])]

    pd_curations = pd_curations.dropna()
    # age at diagnosis (years)

    return pd_curations


def get_manual_curations(attribute_1, attribute_2, user):
    relationships = []
    graph = connect_to_graph()

    results = graph.run('MATCH (a:Attribute {name: "' + attribute_1 + '"})-[r]->'
                        '(b:Attribute {name: "' + attribute_2 + '"}) WHERE r.owner="' + user + '"  RETURN r')

    for relation in results:
        if type(results['r']).__name__ in RelationshipType.get_curation_type_names():
            return type(results['r']).__name__, relation['r']['attribute']

    return None, None


# def get_relationships(attribute_1, attribute_2):
#     relationships = []
#     # graph = GraphDatabase.driver(db_url, auth=(username, password))
#     graph = connect_to_graph()
#
#     results = graph.run("MATCH (:attribute {attribute: 'sample type'})-[r]-"
#                         "(:attribute {attribute: 'vioscreen d total'}) RETURN r")
#     for relation in results:
#         relationships.append((relation['r']))
#
#     return relationships
#
#
# def get_relationships2(attribute_1, attribute_2):
#     relationships = []
#     graph = connect_to_graph()
#
#     node_1 = Node("attribute", attribute=attribute_1)
#     node_2 = Node("attribute", attribute=attribute_2)
#     rel_match = RelationshipMatch(graph, nodes=[node_1, node_2])
#     for relation in rel_match.__iter__():
#         relationships.append(relation)
#
#     return relationships


def add_curation(attribute_1, attribute_2, attribute_curated, user):
    graph = connect_to_graph()

    delete_created_relationships = 'MATCH (a:Attribute {name: "' + attribute_1 + '"})-[r]->(b:Attribute {name: "' + attribute_2 + '"}) ' \
                                   'WHERE (a)-[r:SAME_AS {owner : "' + user + '"}]-(b) ' \
                                        'OR (a)-[r:DIFFERENT_FROM {owner : "' + user + '"}]-(b) ' \
                                        'OR (a)-[r:IGNORES {owner : "' + user + '"}]-(b) ' \
                                   'DELETE r'

    create_relationship = 'MATCH (a:Attribute),(b:Attribute) ' \
                          'WHERE a.name = "' + attribute_1 + '" AND b.name = "' + attribute_2 + '" ' \
                          'CREATE (a)-[r:SAME_AS {owner: "' + user + '", attribute: "' + attribute_curated + '"}]->(b) ' \
                          'RETURN type(r)'
    graph.run(delete_created_relationships)
    graph.run(create_relationship)


def reject_curation(attribute_1, attribute_2, user):
    logging.info("Rejected")
    graph = connect_to_graph()

    delete_created_relationships = 'MATCH (a:Attribute {name: "' + attribute_1 + '"})-[r]->(b:Attribute {name: "' + attribute_2 + '"}) ' \
                                   'WHERE (a)-[r:SAME_AS {owner : "' + user + '"}]-(b) ' \
                                          'OR (a)-[r:DIFFERENT_FROM {owner : "' + user + '"}]-(b) ' \
                                          'OR (a)-[r:IGNORES {owner : "' + user + '"}]-(b) ' \
                                   'DELETE r'

    create_relationship = 'MATCH (a:Attribute),(b:Attribute) ' \
                          'WHERE a.name = "' + attribute_1 + '" AND b.name = "' + attribute_2 + '" ' \
                          'CREATE (a)-[r:DIFFERENT_FROM {owner: "' + user + '"}]->(b) ' \
                          'RETURN type(r)'
    graph.run(delete_created_relationships)
    graph.run(create_relationship)


def ignore_curation(attribute_1, attribute_2, user):
    logging.info("Ignored")
    graph = connect_to_graph()

    delete_created_relationships = 'MATCH (a:Attribute {name: "' + attribute_1 + '"})-[r]->(b:Attribute {name: "' + attribute_2 + '"}) ' \
                                   'WHERE (a)-[r:SAME_AS {owner : "' + user + '"}]-(b) ' \
                                          'OR (a)-[r:DIFFERENT_FROM {owner : "' + user + '"}]-(b) ' \
                                          'OR (a)-[r:IGNORES {owner : "' + user + '"}]-(b) ' \
                                   'DELETE r'

    create_relationship = 'MATCH (a:Attribute),(b:Attribute) ' \
                          'WHERE a.name = "' + attribute_1 + '" AND b.name = "' + attribute_2 + '" ' \
                          'CREATE (a)-[r:IGNORES {owner: "' + user + '"}]->(b) ' \
                          'RETURN type(r)'

    graph.run(delete_created_relationships)
    graph.run(create_relationship)


def create_attribute(attribute):
    graph = connect_to_graph()
    merge_node = "MERGE (a:Attribute {name: '" + attribute.name + "', quality: " + str(attribute.quality) + "}) RETURN a"
    graph.run(merge_node)


def update_attribute_quality(attribute, quality):
    graph = connect_to_graph()
    merge_node = "MATCH (n { name: '" + attribute.name + "' }) SET n.quality = n.quality + 0.5 RETURN n"
    graph.run(merge_node)


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
    graph = Graph(db_url, user=userName, password=password)
    return graph


if __name__ == '__main__':
    # print(len(get_curations(0, 5)))
    # print(len(get_relationships2('sample type', 'vioscreen d total')))
    # usernode = get_user('isuru')
    # print(usernode)
    # relations = get_manual_curations('', '', '')
    # relations = get_suggested_curations(10, 10, '')
    relations = get_manual_curations_all()
    print(relations)
    # print(html.escape("hello' world"))

