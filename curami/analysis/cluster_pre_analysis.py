import json
import pandas as pd
import file_utils
from common_utils import AttributeCleaner

values_count_map = {}
attribute_value_count = {}


def list_values_for_attribute(attribute):
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
    pd_attribute_value_count.to_csv("../../data/results/attribute_values/" + attribute.lower().replace(" ", "_") + ".csv", index=False)


def list_values_for_attributes(attribute_list):
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
        pd_attribute_value_count.to_csv("../../data/results/attribute_values/" + attr.lower().replace(" ", "_") + ".csv", index=False)


def list_values_head_for_attributes():
    with open(file_utils.attribute_values_file, 'r') as input_file:
        attribute_values = json.load(input_file)

    attribute_cleaner = AttributeCleaner()
    attribute_values_head = []
    unique_attr_df = pd.read_csv(file_utils.unique_attributes_file_final).head(1000)
    for index, row in unique_attr_df.iterrows():
        cleaned_attr_list = attribute_cleaner.get_cleaned_attribute_list(row[0])
        values = []
        for attr in cleaned_attr_list:
            if attr in attribute_values:
                values = values + attribute_values[attr]
            if len(values) >= 5:
                continue

        values = values[0:5]
        attribute_values_head.append({"ATTRIBUTE": row[0], "COUNT": row[1],
                                      "VALUE_1": values[0] if len(values) > 0 else "",
                                      "VALUE_2": values[1] if len(values) > 1 else "",
                                      "VALUE_3": values[2] if len(values) > 2 else "",
                                      "VALUE_4": values[3] if len(values) > 3 else "",
                                      "VALUE_5": values[4] if len(values) > 4 else ""})

    pd_attribute_value_count = pd.DataFrame(attribute_values_head,
                                            columns=["ATTRIBUTE", "COUNT", "VALUE_1", "VALUE_2", "VALUE_3", "VALUE_4", "VALUE_5"])
    pd_attribute_value_count.to_csv("../../data/results/attribute_values/attr_value_head_count.csv", index=False)


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
    # list_values_for_attribute('organism part')
    # list_values_for_attributes(['sex', 'gender'])
    # get_attribute_value_types('NCBI submission package')
    list_values_head_for_attributes()

