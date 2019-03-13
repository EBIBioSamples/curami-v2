import json
import os
import numpy as np
import pandas as pd
from tqdm import tqdm

import commons.set_encoder as set_encoder


data_directory = "../data/raw/"
combined_data_directory = "../data/combined/"
intermediate_data_directory = "../data/intermediate/"
intermediate_simple_directory = intermediate_data_directory + "simple/"
intermediate_underscore_directory = intermediate_data_directory + "underscore/"
intermediate_non_word_directory = intermediate_data_directory + "non_word/"
intermediate_clean_directory = intermediate_data_directory + "clean/"
data_extension = ".txt"

all_data_file = intermediate_data_directory + "all_data.csv"
unique_attributes_file = intermediate_data_directory + "unique_attributes.csv"
unique_values_file = intermediate_data_directory + "unique_values.csv"
attribute_values_file = intermediate_data_directory + "attribute_values.json"
summary_file = intermediate_data_directory + "summary.txt"

unique_values_file_simple = intermediate_simple_directory + "unique_attributes.csv"
unique_values_file_simple_diff = intermediate_simple_directory + "unique_attributes_diff.csv"
unique_values_file_underscore = intermediate_underscore_directory + "unique_attributes.csv"
unique_values_file_underscore_diff = intermediate_underscore_directory + "unique_attributes_diff.csv"
unique_values_file_non_word = intermediate_non_word_directory + "unique_attributes.csv"
unique_values_file_non_word_diff = intermediate_non_word_directory + "unique_attributes_diff.csv"

matched_attributes_file = intermediate_data_directory + "matched_attributes.csv"

encoding = "utf-8"


def create_data_directory():
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    if not os.path.exists(combined_data_directory):
        os.makedirs(combined_data_directory)

    if not os.path.exists(intermediate_data_directory):
        os.makedirs(intermediate_data_directory)

    if not os.path.exists(intermediate_simple_directory):
        os.makedirs(intermediate_simple_directory)

    if not os.path.exists(intermediate_underscore_directory):
        os.makedirs(intermediate_underscore_directory)
        os.makedirs(intermediate_simple_directory)

    if not os.path.exists(intermediate_non_word_directory):
        os.makedirs(intermediate_non_word_directory)

    if not os.path.exists(intermediate_clean_directory):
        os.makedirs(intermediate_clean_directory)


def read_from_file(file_no):
    with open(data_directory + str(file_no) + data_extension, "r") as data_file:
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
        with open(combined_data_directory + str(i) + data_extension, "r") as data_file:
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
        with open(combined_data_directory + str(i) + data_extension, "r") as data_file:
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
        with open(combined_data_directory + str(i) + data_extension, "r") as data_file:
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
    with open(data_directory + str(1) + data_extension, "r") as data_file:
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


def combine_files(count):
    file_list = os.listdir(data_directory)
    print("Found " + str(len(file_list)) + " files. Aggregating them into " + str(len(file_list) / count) + " files")
    file_count = 0
    sample_list = []
    for i, file_name in enumerate(sorted(file_list)):  # for consistency we will sort, but not exactly expected order,
        with open(data_directory + file_name, "r") as data_file:
            sample_sub_list = json.load(data_file)
        if ((i + 1) % count) == 0:
            sample_list = sample_list + sample_sub_list
            with open(combined_data_directory + str(file_count) + data_extension, "w") as output:
                output.write(json.dumps(sample_list, indent=4))
            sample_list = []
            file_count = file_count + 1
        else:
            sample_list = sample_list + sample_sub_list

        if not sample_list:
            with open(combined_data_directory + str(file_count) + data_extension, "w") as output:
                output.write(json.dumps(sample_list, indent=4))


def generate_all_intermediate_files(from_file_no, to_file_no):
    data_list = []
    unique_attributes = {}
    unique_values = {}

    attribute_values_map = {}

    print("Reading samples into memory")
    sample_list = []
    for i in range(from_file_no, to_file_no):
        with open(combined_data_directory + str(i) + data_extension, "r") as data_file:
            sample_list = sample_list + json.load(data_file)

    print("Transforming sample data")
    for sample in sample_list:
        data_map = {}

        accession = sample["accession"]
        attribute_values = sample["characteristics"]

        data_map["accession"] = accession
        for key, value_as_list in attribute_values.items():
            value = value_as_list[0]["text"]

            data_map[key] = value

            if key in unique_attributes:
                unique_attributes[key] = unique_attributes[key] + 1
            else:
                unique_attributes[key] = 1

            if value in unique_values:
                unique_values[value] = unique_values[value] + 1
            else:
                unique_values[value] = 1

            if key in attribute_values_map:
                attribute_values_map[key].add(value)
            else:
                attribute_values_map[key] = {value}

        data_list.append(data_map)

    # write everything to files
    print("Writing to files")
    pd_data = pd.DataFrame(data_list)
    pd_data.to_csv(all_data_file, index=False, encoding="utf-8")

    pd_unique_attributes = pd.DataFrame(
        list(sorted(unique_attributes.items(), key=lambda kv: kv[1], reverse=True)),columns=["ATTRIBUTE", "COUNT"])
    pd_unique_attributes.to_csv(unique_attributes_file, index=False, encoding="utf-8")

    pd_unique_values = pd.DataFrame(
        list(sorted(unique_values.items(), key=lambda kv: kv[1], reverse=True)), columns=["VALUE", "COUNT"])
    pd_unique_values.to_csv(unique_values_file, index=False, encoding="utf-8")

    with open(attribute_values_file, "w") as output:
        output.write(json.dumps(attribute_values_map, indent=4, cls=set_encoder.SetEncoder))

    # generate summary and write to file
    summary = dict()
    summary["samples #"] = len(data_list)
    summary["attribute/value #"] = sum(unique_attributes.values())
    summary["unique attribute #"] = len(unique_attributes)
    summary["unique value #"] = len(unique_values)
    with open(summary_file, "w") as output:
        output.write(json.dumps(summary, indent=4))


if __name__ == "__main__":
    create_data_directory()
    combine_files(100)
    # generate_all_intermediate_files(1, 2)
    # print(len(get_all_attributes(1, 6)))
