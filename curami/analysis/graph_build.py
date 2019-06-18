import sys
from neo4j import GraphDatabase
import file_utils
from py2neo import Node, Graph, Relationship
import pandas as pd

uri = "bolt://localhost:7687"
userName = "neo4j"
password = "neo5j"


def build_graph_1():
    graphDB_Driver = GraphDatabase.driver(uri, auth=(userName, password))

    cqlNodeQuery = "MATCH (x:attribute) RETURN x"
    cqlEdgeQuery = "MATCH (x:attribute {name:'sample source name attribute'})-[r]->(y:attribute) RETURN y.name,r.correlation"

    cqlCreate = """CREATE 
        (Organism:attribute { name: "Organism attribute"}),
        (sample_source_name:attribute { name: "sample source name attribute"}),
        (disease:attribute { name: "disease attribute"}),
        (description:attribute { name: "description attribute"}),
        
        (Organism)-[:cooccurs_with {correlation: 259}]->(sample_source_name),
        (Organism)-[:cooccurs_with {correlation: 210}]->(disease),
        (Organism)-[:cooccurs_with {correlation: 327}]->(description),
    
        (sample_source_name)-[:cooccurs_with {correlation: 259}]->(Organism),
        (sample_source_name)-[:cooccurs_with {correlation: 133}]->(disease),
        (sample_source_name)-[:cooccurs_with {correlation: 133}]->(description),
        
        (description)-[:cooccurs_with {correlation: 327}]->(Organism),
        (description)-[:cooccurs_with {correlation: 133}]->(sample_source_name),
        (description)-[:cooccurs_with {correlation: 260}]->(disease),
        
        (disease)-[:cooccurs_with {correlation: 210}]->(Organism),
        (disease)-[:cooccurs_with {correlation: 133}]->(sample_source_name),
        (disease)-[:cooccurs_with {correlation: 260}]->(description)
        """

    with graphDB_Driver.session() as graphDB_Session:
        graphDB_Session.run(cqlCreate)

        nodes = graphDB_Session.run(cqlNodeQuery)
        print("List of Ivy League universities present in the graph:")
        for node in nodes:
            print(node)

        nodes = graphDB_Session.run(cqlEdgeQuery)
        print("Distance from sample source name attribute to the other Ivy League universities present in the graph:")
        for node in nodes:
            print(node)


def build_graph():
    attributes_pd = pd.read_csv(file_utils.unique_attributes_file, encoding=file_utils.encoding)
    coexistance_pd = pd.read_csv(file_utils.coexistance_file, encoding=file_utils.encoding)

    graph = Graph(uri, user=userName, password=password)
    # graph.delete_all()

    attribute_map = {}
    for index, row in attributes_pd.iterrows():
        attribute_map[row["ATTRIBUTE"]] = row["COUNT"]

    for index, row in coexistance_pd.iterrows():
        node1_name = row["ATTRIBUTE_1"]
        node2_name = row["ATTRIBUTE_2"]
        correlation = row["COUNT"]

        node1 = Node("attribute", count=attribute_map[node1_name], attribute=node1_name)
        node2 = Node("attribute", count=attribute_map[node2_name], attribute=node2_name)
        node1_node2 = Relationship(node1, "cooccurs_with", node2, correlation=correlation)

        graph.merge(node1_node2, "attribute", "attribute")

    # node = Node("attribute", )

def main(*args):
    build_graph()


if __name__ == "__main__":
    main(*sys.argv[1:])
