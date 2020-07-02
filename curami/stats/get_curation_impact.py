import json
import sys

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# import sys
# sys.path.append("/home/isuru/Projects/curami-v2")
# export PYTHONPATH=/home/isuru/Projects/curami-v2

from curami.commons import file_utils

sample_count_string = "total samples"
av_count_string = "total attributes"
unique_attribute_count_string = "unique attribute count"
unique_value_count_string = "unique value count"


def plot_data_growth():
    # attribute_count = pd.read_csv(file_utils.unique_attributes_file, index_col='ATTRIBUTE')
    attribute_count = pd.read_csv(file_utils.unique_attributes_file)
    curation_rules = pd.read_csv(file_utils.curation_rules_file)

    attribute_count_dict = {}
    for index, row in attribute_count.iterrows():
        attribute_count_dict[row[0]] = row[1]

    curation_rule_impact = {}
    for index, row in curation_rules.iterrows():
        count = attribute_count_dict[row[0]]
        curation_rule_impact[row[0]] = count

    curation_rule_impact_2 = {k: v for k, v in sorted(curation_rule_impact.items(), key=lambda item: item[1], reverse=True)}

    # curation_rule_impact_pd = pd.DataFrame(curation_rule_impact, columns=['a', 'b'])
    print('hello')





def main(*args):
    plot_data_growth()


if __name__ == "__main__":
    main(*sys.argv[1:])
