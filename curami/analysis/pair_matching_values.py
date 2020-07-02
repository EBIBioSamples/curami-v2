import json

import pandas as pd

from curami.commons import file_utils

'''
Match pair of attributes for their value similarity
'''

match_ratio = 0.75


def analyze():
    with open(file_utils.attribute_values_file, 'r') as input_file:
        attribute_values = json.load(input_file)

    matched_attributes = []
    attributes = pd.read_csv(file_utils.matched_attributes_file, encoding=file_utils.encoding)
    for index, row in attributes.iterrows():
        if row["ATTRIBUTE_1"] in attribute_values and row["ATTRIBUTE_2"] in attribute_values:
            value_list_1 = attribute_values[row["ATTRIBUTE_1"]]
            value_list_2 = attribute_values[row["ATTRIBUTE_2"]]
            intersection = len(set(value_list_1) & set(value_list_2))
            union = len(set(value_list_1).union(set(value_list_2)))
            score = intersection / union

            if score > match_ratio:
                matched_attributes.append({"ATTRIBUTE_1": row["ATTRIBUTE_1"],
                                           "ATTRIBUTE_2": row["ATTRIBUTE_2"],
                                           "RATIO": score})

    pd_matched_attributes = pd.DataFrame(matched_attributes)
    pd_matched_attributes = pd_matched_attributes.sort_values(by="RATIO", ascending=False)
    pd_matched_attributes.to_csv(
        file_utils.value_matched_attribute_file, index=False, encoding=file_utils.encoding)


if __name__ == "__main__":
    analyze()
