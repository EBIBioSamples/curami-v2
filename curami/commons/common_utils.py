import pandas as pd

from curami.commons import file_utils


def build_attribute_map():
    attributes_pd = pd.read_csv(file_utils.unique_attributes_file_final, encoding=file_utils.encoding)
    attribute_map = {}
    for index, row in attributes_pd.iterrows():
        attribute_map[row["ATTRIBUTE"]] = row["COUNT"]

    print("Loaded " + str(len(attributes_pd)) + " unique attributes")
    return attribute_map
