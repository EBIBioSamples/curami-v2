import json
import os
import pathlib

status_file = "../../data/status.json"
data_directory = "../../data/raw/"  # todo remove
combined_data_directory = "../../data/combined/"  # todo remove
data_sample_directory = "../../data/sample/"  # todo remove
raw_sample_directory = "../../data/samples/"
raw_sample_directory_temp = "../../data/samples/temp/"
intermediate_data_directory = "../../data/intermediate/"
results_directory = "../../data/results/"
intermediate_simple_directory = intermediate_data_directory + "simple/"
intermediate_underscore_directory = intermediate_data_directory + "underscore/"
intermediate_clean_directory = intermediate_data_directory + "clean/"
data_extension = ".txt"

all_data_file = intermediate_data_directory + "all_data.csv"
unique_attributes_file = intermediate_data_directory + "unique_attributes.csv"
unique_values_file = intermediate_data_directory + "unique_values.csv"
attribute_values_file = intermediate_data_directory + "attribute_values.json"
summary_file = intermediate_data_directory + "summary.txt"
coexistence_file = intermediate_data_directory + "coexistence.csv"

unique_attributes_file_final_diff = results_directory + "unique_attributes_diff.csv"
unique_attributes_file_final_diff_all = results_directory + "unique_attributes_diff_all.csv"
unique_attributes_file_final = results_directory + "unique_attributes.csv"
coexistence_file_final = results_directory + "coexistence.csv"

matched_attributes_file = intermediate_data_directory + "matched_attributes.csv"
matched_synonym_attributes_file = intermediate_data_directory + "matched_synonym_attributes.csv"
dictionary_matched_attribute_file = results_directory + "dictionary_matched.csv"
word_base_matched_attribute_file = results_directory + "word_base_matched.csv"
value_matched_attribute_file = results_directory + "value_matched.csv"

coexistence_probability_file = results_directory + "coexistence_probability.csv"
curation_rules_file = results_directory + "curation_rules.csv"
clustered_samples_file = results_directory + "clustered_samples.csv"

gephi_network_file = results_directory + "coexistence_network.gexf"

encoding = "utf-8"


def create_data_directory():
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    if not os.path.exists(raw_sample_directory):
        os.makedirs(raw_sample_directory)

    if not os.path.exists(raw_sample_directory_temp):
        os.makedirs(raw_sample_directory_temp)

    if not os.path.exists(combined_data_directory):
        os.makedirs(combined_data_directory)

    if not os.path.exists(intermediate_data_directory):
        os.makedirs(intermediate_data_directory)

    if not os.path.exists(intermediate_simple_directory):
        os.makedirs(intermediate_simple_directory)

    pathlib.Path(intermediate_underscore_directory).mkdir(parents=True, exist_ok=True)
    pathlib.Path(intermediate_simple_directory).mkdir(parents=True, exist_ok=True)

    if not os.path.exists(intermediate_clean_directory):
        os.makedirs(intermediate_clean_directory)

    if not os.path.exists(results_directory):
        os.makedirs(results_directory)


def read_from_file(file_no):
    with open(raw_sample_directory + str(file_no) + data_extension, "r") as data_file:
        # input_string = input.read()
        sample_list = json.load(data_file)
    return sample_list


def read_from_files(from_file_no, to_file_no):
    return


def write_to_file(file_no, content):
    return


def get_all_attributes(from_file_no, to_file_no):
    attribute_list = []
    sample_list = []
    for i in range(from_file_no, to_file_no):
        with open(raw_sample_directory + str(i) + data_extension, "r") as data_file:
            sample_list = sample_list + json.load(data_file)

    for sample in sample_list:
        accession = sample["accession"]
        attribute_values = sample["characteristics"]
        attributes = list(attribute_values.keys())

        attribute_list.append(attributes)

    return attribute_list


def get_all_values(from_file_no, to_file_no):
    value_list = []
    sample_list = []
    for i in range(from_file_no, to_file_no):
        with open(raw_sample_directory + str(i) + data_extension, "r") as data_file:
            sample_list = sample_list + json.load(data_file)

    for sample in sample_list:
        accession = sample["accession"]
        attribute_values = sample["characteristics"]

        values = []
        for value in attribute_values.values():
            text_value = value[0]["text"]
            values.append(text_value)

        value_list.append(values)

    return value_list


def get_key_value_as_features(from_file_no, to_file_no):
    value_list = []
    sample_list = []
    for i in range(from_file_no, to_file_no):
        with open(raw_sample_directory + str(i) + data_extension, "r") as data_file:
            sample_list = sample_list + json.load(data_file)

    for sample in sample_list:
        accession = sample["accession"]
        attribute_values = sample["characteristics"]

        values = []
        for value in attribute_values.values():
            text_value = value[0]["text"]
            values.append(text_value)

        value_list.append(values)

    return value_list


def get_key_value_as_features1():
    with open(raw_sample_directory + str(1) + data_extension, "r") as data_file:
        sample_list = json.load(data_file)

    for sample in sample_list:
        accession = sample["accession"]
        attribute_values = sample["characteristics"]

        attributes = list(attribute_values.keys())

        values = []
        for value in attribute_values.values():
            text_value = value[0]["text"]
            values.append(text_value)

        key_value_pairs = {}
        for key, value in attribute_values.items():
            key_value_pairs[key] = value[0]["text"]

        print(key_value_pairs)

    print(len(sample_list))




if __name__ == "__main__":
    create_data_directory()
    # generate_all_intermediate_files(1, 2)
    # print(len(get_all_attributes(1, 6)))
