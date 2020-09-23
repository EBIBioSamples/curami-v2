import pandas as pd
import file_utils

from neo4j import GraphDatabase
from curami.commons.config_params import NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD


class GraphBuilder(object):

    def __init__(self, _uri, _user, _password):
        if _user:
            self._driver = GraphDatabase.driver(_uri, auth=(_user, _password), encrypted=False)
        else:
            self._driver = GraphDatabase.driver(_uri)

    def load_attributes(self, attribute_file_path):
        attributes_pd = pd.read_csv(attribute_file_path, encoding=file_utils.encoding)
        with self._driver.session() as session:
            for index, row in attributes_pd.iterrows():
                session.write_transaction(
                    GraphBuilder._create_attribute, row["ATTRIBUTE"], row["COUNT"])

    def load_values(self, value_file_path):
        values_pd = pd.read_csv(value_file_path, encoding=file_utils.encoding)
        print("Number of unique attributes to load: " + str(len(values_pd.index)))
        with self._driver.session() as session:
            for index, row in values_pd.iterrows():
                session.write_transaction(
                    GraphBuilder._create_value, row["VALUE"], row["COUNT"])

    def clear_graph(self):
        with self._driver.session() as session:
            session.write_transaction(self._delete_all)

    @staticmethod
    def _create_attribute(tx, _name, _frequency):
        # tx.run("MERGE (a:Attribute{name:$name}) SET a.frequency=$frequency", name=_name, frequency=_frequency)
        tx.run("MERGE (a:Attribute {name:\"" + str(_name) + "\"}) SET a.frequency=" + str(_frequency))

    @staticmethod
    def _create_value(tx, _name, _frequency):
        _name = str(_name).replace("\\", "/").replace("\"", "'")
        tx.run("MERGE (a:Value {name:\"" + str(_name) + "\"}) SET a.frequency=" + str(_frequency))

    @staticmethod
    def _add_relationship(tx, _source, _target, _relation_name):
        name = "r:" + "_".join(_relation_name.upper().split(" "))
        tx.run("MERGE (a:Attribute{name:$_source}) MERGE (b:Attribute{name:$_target}) MERGE (a)-[r:$name]->(b)",
               source=_source, target=_target, name=name)

    @staticmethod
    def _delete_all(tx):
        tx.run("MATCH (n) DETACH DELETE n")


if __name__ == "__main__":
    graph_builder = GraphBuilder(NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD)
    # graph_builder.clear_graph()
    # graph_builder.load_attributes(file_utils.unique_attributes_file_final)
    graph_builder.load_values(file_utils.unique_values_file)

