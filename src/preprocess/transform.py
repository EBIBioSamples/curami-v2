import json
import pandas as pd
from tqdm import tqdm

from src import commons as file_utils
import set_encoder as set_encoder


def transform():
    print("Transforming data")
    from_file_no = 1
    to_file_no = 250
    # generate_attribute_value_files(from_file_no, to_file_no)
    generate_all_data_file(from_file_no, to_file_no)


def generate_attribute_value_files(from_file_no, to_file_no):
    print("Generating attribute, value files in " + file_utils.intermediate_data_directory)
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

    print("Writing to files")
    pd_unique_attributes = pd.DataFrame(
        list(sorted(unique_attributes.items(), key=lambda kv: kv[1], reverse=True)), columns=["ATTRIBUTE", "COUNT"])
    pd_unique_attributes.to_csv(file_utils.unique_attributes_file, index=False, encoding="utf-8")

    pd_unique_values = pd.DataFrame(
        list(sorted(unique_values.items(), key=lambda kv: kv[1], reverse=True)), columns=["VALUE", "COUNT"])
    pd_unique_values.to_csv(file_utils.unique_values_file, index=False, encoding="utf-8")

    with open(file_utils.attribute_values_file, "w") as output:
        output.write(json.dumps(attribute_values_map, indent=4, cls=set_encoder.SetEncoder))

    # generate summary and write to file
    print("Writing summary to file")
    summary = dict()
    summary["total samples"] = total_samples
    summary["total attributes"] = sum(unique_attributes.values())
    summary["unique attribute count"] = len(unique_attributes)
    summary["unique value count"] = len(unique_values)
    with open(file_utils.summary_file, "w") as output:
        output.write(json.dumps(summary, indent=4))


def generate_all_data_file(from_file_no, to_file_no):
    # generating all data file, seems like this file is too large with lot of sparce data
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
    transform()
    # a = {"a": "1", "b": "2"}
    # b = {"b": "3", "c": "4"}
    # c = {"d": "5", "e": "6", "f": "6"}
    # d = {"a": "5", "e": "6", "g": "6"}
    #
    #
    # c1 = {"a": "5", "b": "2", "c": "3"}
    #
    # list1 = list(c1.items())
    # data_frame = pd.DataFrame(list1, columns=["x", "y"])
    # columns = data_frame["x"].tolist()
    #
    # with open("../data/test.text", "a") as out:
    #     l = [d]
    #     pd_1 = pd.DataFrame(l, columns=["a", "b", "c", "d", "e", "f", "g"])
    #     pd_1.to_csv(out, index=False, encoding="utf-8")
    #
    # with open("../data/test.text", "w") as out:
    #     l = [c]
    #     pd_1 = pd.DataFrame(l, columns=["a", "b", "c", "d", "e", "f"])
    #     pd_1.to_csv(out, index=False, encoding="utf-8")
    #
    # with open("../data/test.text", "a") as out:
    #     l = [a]
    #     pd_1 = pd.DataFrame(l, columns=["a", "b", "c", "d", "e", "f"])
    #     pd_1.to_csv(out, header=False, index=False, encoding="utf-8")


