import sys

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

import file_utils
from curami.commons import neo4j_connector


def build_neo4j_curation_graph():
    neo4j_conn = neo4j_connector.Neo4jConnector()
    neo4j_conn.build_curation_graph(file_utils.dictionary_matched_attribute_file, True)


def build_neo4j_cooccurance_graph():
    neo4j_conn = neo4j_connector.Neo4jConnector()
    neo4j_conn.build_cooccurance_graph(file_utils.coexistence_file_final, True)


def build_gephi_coexistence_graph():
    coexistence_df = pd.read_csv(file_utils.coexistence_probability_file, encoding=file_utils.encoding)

    coexistence_df_head = coexistence_df.head(100000)
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


def main(*args):
    build_neo4j_curation_graph()


if __name__ == "__main__":
    main(*sys.argv[1:])
