import sys

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from py2neo import Node, Relationship
from tqdm import tqdm

import file_utils
from curami.commons import neo4j_connector

from multiprocessing import pool


def build_curation_graph():
    neo4j_conn = neo4j_connector.Neo4jConnector()
    neo4j_conn.build_curation_graph(file_utils.dictionary_matched_attribute_file, True)


def build_cooccurance_graph2():
    coexistence_pd = pd.read_csv(file_utils.coexistence_file_final, encoding=file_utils.encoding)
    print("Loading " + str(len(coexistence_pd)) + " Links from coexistence file")

    graph = neo4j_connector.connect_to_graph()
    graph.delete_all()

    attribute_map = build_attribute_map()

    progress_bar = tqdm(total=len(coexistence_pd))
    for index, row in coexistence_pd.iterrows():
        node1_name = row["ATTRIBUTE_1"]
        node2_name = row["ATTRIBUTE_2"]
        correlation = row["COUNT"]

        node1 = Node("Attribute", name=node1_name, count=attribute_map[node1_name], quality=0)
        node2 = Node("Attribute", name=node2_name, count=attribute_map[node2_name], quality=0)
        node1_node2 = Relationship(node1, "COOCCURS_WITH", node2, correlation=correlation)

        graph.merge(node1_node2, "name", "name")
        progress_bar.update(1)

    print("Finished loading data into neo4j")


def build_cooccurance_graph():
    coexistence_pd = pd.read_csv(file_utils.coexistence_file_final, encoding=file_utils.encoding)
    print("Loading " + str(len(coexistence_pd)) + " Links from coexistence file")

    graph = neo4j_connector.connect_to_graph()
    graph.delete_all()

    attribute_map = build_attribute_map()

    progress_bar = tqdm(total=len(coexistence_pd))
    job_list = []
    job_list_size = 1000
    p = pool.Pool(processes=8)

    for index, row in coexistence_pd.iterrows():
        if (index + 1) % job_list_size == 0:
            results = p.map(persist_relationship, job_list)
            for result in results:
                progress_bar.update(1)
            job_list = []
        else:
            job_list.append([row["ATTRIBUTE_1"], row["ATTRIBUTE_2"], row["COUNT"], attribute_map, graph])

    print("Finished loading data into neo4j")


def persist_relationship(node1_name, node2_name, correlation, attribute_map, graph):
    node1 = Node("Attribute", name=node1_name, count=attribute_map[node1_name], quality=0)
    node2 = Node("Attribute", name=node2_name, count=attribute_map[node2_name], quality=0)
    node1_node2 = Relationship(node1, "COOCCURS_WITH", node2, correlation=correlation)

    graph.merge(node1_node2, "name", "name")


def generate_visualisation_formats():
    coexistence_df = pd.read_csv(file_utils.coexistence_probability_file, encoding=file_utils.encoding)

    coexistence_df_head = coexistence_df.head(100000)
    # coexistence_df_head = coexistence_df.head(100000).filter(like='', axis=0)
    coexistence_df_head = coexistence_df_head[~coexistence_df_head["ATTRIBUTE_1"].str.contains("vioscreen")]
    coexistence_df_head = coexistence_df_head[~coexistence_df_head["ATTRIBUTE_2"].str.contains("vioscreen")]

    graph = nx.Graph()
    graph = nx.from_pandas_edgelist(coexistence_df_head,
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


def build_attribute_map():
    attributes_pd = pd.read_csv(file_utils.unique_attributes_file_final, encoding=file_utils.encoding)
    attribute_map = {}
    for index, row in attributes_pd.iterrows():
        attribute_map[row["ATTRIBUTE"]] = row["COUNT"]

    print("Loaded " + str(len(attributes_pd)) + " unique attributes")
    return attribute_map


def generate_visualisation_formats_1():
    coexistence_df = pd.read_csv(file_utils.coexistence_probability_file, encoding=file_utils.encoding)

    # coexistence_df_head = coexistence_df.head(100000)
    # # coexistence_df_head = coexistence_df.head(100000).filter(like='', axis=0)
    # coexistence_df_head = coexistence_df_head[~coexistence_df_head["ATTRIBUTE_1"].str.contains("vioscreen")]
    # coexistence_df_head = coexistence_df_head[~coexistence_df_head["ATTRIBUTE_2"].str.contains("vioscreen")]

    coexistence_df_row = coexistence_df[(coexistence_df["ATTRIBUTE_1"] == "altitude") & (coexistence_df["ATTRIBUTE_2"] == "latitude")]
    print(coexistence_df_row)


def main(*args):
    # build_cooccurance_graph()
    build_curation_graph()
    # generate_visualisation_formats_1()


if __name__ == "__main__":
    main(*sys.argv[1:])
