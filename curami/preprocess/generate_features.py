import json
import pandas as pd
from tqdm import tqdm

from curami.commons import file_utils
from curami.preprocess.clean import AttributeCleaner


def generate_features_file(from_file_no, to_file_no):
    pd_unique_attributes = pd.read_csv(file_utils.unique_attributes_file_final)
    columns = pd_unique_attributes["ATTRIBUTE"][0:1000].tolist()
    columns_set = set(columns)
    attribute_cleaner = AttributeCleaner()
    data_list = []

    for i in tqdm(range(from_file_no, to_file_no + 1)):
        with open(file_utils.combined_data_directory + str(i) + file_utils.data_extension, "r") as data_file:
            sample_list = json.load(data_file)

        for sample in sample_list:
            attribute_values = sample["characteristics"]

            data_map = {"accession": sample["accession"]}
            for key, value_as_list in attribute_values.items():
                cleaned_key = attribute_cleaner.get_clean_attribute(key)
                if cleaned_key in columns_set:
                    data_map[cleaned_key] = int(1)

            data_list.append(data_map)

    pd_data_list = pd.DataFrame(data_list, columns=columns.append("accession"))
    pd_data_list.fillna(int(0), inplace=True)
    with open(file_utils.all_data_file, 'w') as output:
        pd_data_list.to_csv(output, index=False, encoding="utf-8", float_format='%.0f')


generate_features_file(1, 1)
