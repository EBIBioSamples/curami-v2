import sys
from neo4j import GraphDatabase
from tqdm import tqdm
import networkx as nx
import matplotlib.pyplot as plt

import file_utils
from py2neo import Node, Graph, Relationship
import pandas as pd

uri = "bolt://localhost:7687"
userName = "neo4j"
password = "neo5j"


def build_graph_for_curation():
    attribute_misspelling_df = pd.read_csv(file_utils.dictionary_matched_attribute_file, encoding=file_utils.encoding)

    graph = Graph(uri, user=userName, password=password)
    graph.delete_all()

    for index, row in attribute_misspelling_df.iterrows():
        node1_name = row[0]
        node2_name = row[1]
        probability = row[2]

        node1 = Node("attribute", attribute=node1_name)
        node2 = Node("attribute", attribute=node2_name)
        node1_node2 = Relationship(node1, "looks_similar", node2, probability=probability)

        graph.merge(node1_node2, "attribute", "attribute")

    print("Finished loading data into neo4j")


def build_graph():
    attributes_pd = pd.read_csv(file_utils.unique_attributes_file_final, encoding=file_utils.encoding)
    coexistence_pd = pd.read_csv(file_utils.coexistence_file_final, encoding=file_utils.encoding)
    print("Loading " + str(len(attributes_pd)) + " Attributes and " + str(len(coexistence_pd)) + " Links")

    graph = Graph(uri, user=userName, password=password)
    graph.delete_all()

    attribute_map = {}
    for index, row in attributes_pd.iterrows():
        attribute_map[row["ATTRIBUTE"]] = row["COUNT"]

    progress_bar = tqdm(total=len(coexistence_pd))
    for index, row in coexistence_pd.iterrows():
        node1_name = row["ATTRIBUTE_1"]
        node2_name = row["ATTRIBUTE_2"]
        correlation = row["COUNT"]

        node1 = Node("attribute", count=attribute_map[node1_name], attribute=node1_name)
        node2 = Node("attribute", count=attribute_map[node2_name], attribute=node2_name)
        node1_node2 = Relationship(node1, "cooccurs_with", node2, correlation=correlation)

        graph.merge(node1_node2, "attribute", "attribute")
        progress_bar.update(1)

    print("Finished loading data into neo4j")

    # node = Node("attribute", )


def generate_visualisation_formats():
    coexistence_df = pd.read_csv(file_utils.coexistence_probability_file, encoding=file_utils.encoding)
    graph = nx.Graph()
    graph = nx.from_pandas_edgelist(coexistence_df.head(100000),
                                    source="ATTRIBUTE_1", target="ATTRIBUTE_2",
                                    edge_attr=["COEXISTENCE_COUNT", "DIFF_WEIGHT", "DIFF_COEXISTENCE_ABS"])

    attribute_count_df = pd.read_csv(file_utils.unique_attributes_file_final, encoding=file_utils.encoding)

    attribute_count = {}
    for index, row in attribute_count_df.iterrows():
        attribute_count[row[0]] = {'WEIGHT': row[1]}


    # attribute_count_df['WEIGHT'] = 'WEIGHT'
    # attribute_count = attribute_count_df.set_index('ATTRIBUTE').to_dict()
    # attribute_count = dict(zip(attribute_count_df.ATTRIBUTE, attribute_count_df.COUNT))

    # graph = nx.set_node_attributes(graph, attribute_count)

    nx.write_gexf(graph, file_utils.gephi_network_file)

    nx.draw(graph)
    plt.show()


def main(*args):
    # build_graph()
    build_graph_for_curation()
    # generate_visualisation_formats()


if __name__ == "__main__":
    main(*sys.argv[1:])
