import json
import pandas as pd
import file_utils

values_count_map = {}
attribute_value_count = {}


def get_attribute_value_types(attribute):
    with open(file_utils.attribute_values_file, 'r') as input_file:
        attribute_values = json.load(input_file)
        print(len(attribute_values[attribute]))
        attribute_values = set(attribute_values[attribute])

    pd_unique_values = pd.read_csv(file_utils.unique_values_file)
    attribute_value_count = {}
    for index, row in pd_unique_values.iterrows():
        if row[0] in attribute_values:
            attribute_value_count[row[0]] = row[1]

    del pd_unique_values

    pd_attribute_value_count = pd.DataFrame(list(attribute_value_count.items()), columns=["ATTRIBUTE_VALUE", "COUNT"])
    pd_attribute_value_count.to_csv("../../data/results/" + attribute.lower().replace(" ", "_") + ".csv", index=False)


def get_attribute_value_types_1(attribute_list):
    attribute_value_count_dic = {}
    attribute_value_set_dic = {}
    with open(file_utils.attribute_values_file, 'r') as input_file:
        attribute_values = json.load(input_file)
        for attr in attribute_list:
            attribute_value_set_dic[attr] = set(attribute_values[attr])
            attribute_value_count_dic[attr] = {}
            print(attr + " : " + str(len(attribute_values[attr])))
    del attribute_values

    pd_unique_values = pd.read_csv(file_utils.unique_values_file)
    for index, row in pd_unique_values.iterrows():
        for attr in attribute_list:
            if row[0] in attribute_value_set_dic[attr]:
                attribute_value_count_dic[attr][row[0]] = row[1]

    del pd_unique_values

    for attr in attribute_list:
        pd_attribute_value_count = pd.DataFrame(list(attribute_value_count_dic[attr].items()), columns=["ATTRIBUTE_VALUE", "COUNT"])
        pd_attribute_value_count.to_csv("../../data/results/" + attr.lower().replace(" ", "_") + ".csv", index=False)


def main():
    with open(file_utils.attribute_values_file, 'r') as input_file:
        attribute_values = json.load(input_file)
        print(len(attribute_values["INSDC center name"]))
        attribute_values = set(attribute_values["INSDC center name"])

    pd_unique_values = pd.read_csv(file_utils.unique_values_file)
    attribute_value_count = {}
    for index, row in pd_unique_values.iterrows():
        if row[0] in attribute_values:
            attribute_value_count[row[0]] = row[1]

    del pd_unique_values

    pd_attribute_value_count = pd.DataFrame(list(attribute_value_count.items()), columns=["CENTER", "COUNT"])
    pd_attribute_value_count.to_csv("../../data/results/center_name.csv")
    print("done")


if __name__ == "__main__":
    # main()
    # get_attribute_value_types('study name')
    get_attribute_value_types_1(['study design', 'submitter handle', 'biospecimen repository', 'geographic location', 'ENA checklist'])
    # get_attribute_value_types('NCBI submission package')

