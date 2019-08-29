import json
import logging

import pandas as pd
from tqdm import tqdm

from curami.commons import file_utils
from curami.commons import set_encoder

''' Transform collected data
Data collected are transformed into formats that are easier to analyze.
This process generate following files
- attribute value file
- unique attribute file
- unique value file
- attribute coexistence file
- all data file (this file is too big and not really useful, therefore commented out)
'''


def preprocess():
    logging.info("Transforming data")
    from_file_no = 0
    to_file_no = 106  # inclusive
    generate_attribute_value_files(from_file_no, to_file_no)  # unique attributes, unique values, attribute-values files
    generate_coexistence_file(from_file_no, to_file_no)
    # generate_all_data_file(from_file_no, to_file_no)  # this file is too big, difficult to process
    logging.info("Finished generating all the files")


def generate_attribute_value_files(from_file_no, to_file_no):
    logging.info("Generating attribute, value files")
    unique_attributes = {}
    unique_values = {}
    attribute_values_map = {}
    total_samples = 0

    for i in tqdm(range(from_file_no, to_file_no + 1)):
        with open(file_utils.combined_data_directory + str(i) + file_utils.data_extension, "r") as data_file:
            sample_list = json.load(data_file)

        for sample in sample_list:
            total_samples += 1
            attribute_values = sample["characteristics"]
            for key, value_as_list in attribute_values.items():
                value = value_as_list[0]["text"]

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

    logging.info("Writing attribute, value files in %s", file_utils.intermediate_data_directory)
    pd_unique_attributes = pd.DataFrame(
        list(sorted(unique_attributes.items(), key=lambda kv: kv[1], reverse=True)), columns=["ATTRIBUTE", "COUNT"])
    pd_unique_attributes.to_csv(file_utils.unique_attributes_file, index=False, encoding="utf-8")

    pd_unique_values = pd.DataFrame(
        list(sorted(unique_values.items(), key=lambda kv: kv[1], reverse=True)), columns=["VALUE", "COUNT"])
    pd_unique_values.to_csv(file_utils.unique_values_file, index=False, encoding="utf-8")

    with open(file_utils.attribute_values_file, "w") as output:
        output.write(json.dumps(attribute_values_map, indent=4, cls=set_encoder.SetEncoder))

    # generate summary and write to file
    logging.info("Writing summary to file")
    summary = dict()
    summary["total samples"] = total_samples
    summary["total attributes-value count"] = sum(unique_attributes.values())
    summary["unique attribute count"] = len(unique_attributes)
    summary["unique value count"] = len(unique_values)
    with open(file_utils.summary_file, "w") as output:
        output.write(json.dumps(summary, indent=4))


def generate_coexistence_file(from_file_no, to_file_no):
    logging.info("Generating coexistence file")

    coexistence_map = {}

    for i in tqdm(range(from_file_no, to_file_no + 1)):
        with open(file_utils.combined_data_directory + str(i) + file_utils.data_extension, "r") as data_file:
            sample_list = json.load(data_file)

        for sample in sample_list:
            attribute_values = sample["characteristics"]
            sample_attribute_list = list(attribute_values.keys())

            for i, outer_attribute in enumerate(sample_attribute_list):
                for inner_attribute in sample_attribute_list[i + 1:]:
                    attribute1 = outer_attribute
                    attribute2 = inner_attribute

                    if outer_attribute > inner_attribute:
                        attribute1 = inner_attribute
                        attribute2 = outer_attribute

                    combined_key = attribute1 + "~" + attribute2

                    if combined_key not in coexistence_map:
                        coexistence_map[combined_key] = {"ATTRIBUTE_1": attribute1, "ATTRIBUTE_2": attribute2,
                                                         "COUNT": 0}

                    coexistence_map[combined_key]["COUNT"] = coexistence_map[combined_key]["COUNT"] + 1

    logging.info("Writing coexistence file in %s", file_utils.intermediate_data_directory)
    pd_unique_attributes = pd.DataFrame(
        list(sorted(coexistence_map.values(), key=lambda kv: kv["COUNT"], reverse=True)),
        columns=["ATTRIBUTE_1", "ATTRIBUTE_2", "COUNT"])
    pd_unique_attributes.to_csv(file_utils.coexistence_file, index=False, encoding="utf-8")


def generate_all_data_file(from_file_no, to_file_no):
    # generating all data file, seems like this file is too large with lot of sparse data
    pd_unique_attributes = pd.read_csv(file_utils.unique_attributes_file)
    columns = pd_unique_attributes["ATTRIBUTE"][0:100].tolist()
    columns_set = set(columns)
    # data_list = []
    for i in tqdm(range(from_file_no, to_file_no + 1)):
        with open(file_utils.combined_data_directory + str(i) + file_utils.data_extension, "r") as data_file:
            sample_list = json.load(data_file)

        data_list = []
        for sample in sample_list:
            attribute_values = sample["characteristics"]

            data_map = {"accession": sample["accession"]}
            for key, value_as_list in attribute_values.items():
                if key in columns_set:
                    value = value_as_list[0]["text"]
                    # data_map[key] = value
                    data_map[key] = int(1)

            data_list.append(data_map)

        append = "a"
        if i == from_file_no:
            append = "w"

        pd_data_list = pd.DataFrame(data_list, columns=columns)
        pd_data_list.fillna(int(0), inplace=True)

        if i == from_file_no:
            with open(file_utils.all_data_file, append) as output:
                pd_data_list.to_csv(output, index=False, encoding="utf-8", float_format='%.0f')
        else:
            with open(file_utils.all_data_file, append) as output:
                pd_data_list.to_csv(output, index=False, header=None, encoding="utf-8", float_format='%.0f')

    # pd_data_list = pd.DataFrame(data_list, columns=columns).to_sparse()
    # with open(file_utils.all_data_file, "w") as output:
    #     pd_data_list.to_csv(output, index=False, encoding="utf-8")
    # print(pd_data_list.head())


if __name__ == "__main__":
    preprocess()
