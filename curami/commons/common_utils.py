import pandas as pd

from curami.commons import file_utils


def build_attribute_map():
    attributes_pd = pd.read_csv(file_utils.unique_attributes_file_final, encoding=file_utils.encoding)
    attribute_map = {}
    for index, row in attributes_pd.iterrows():
        attribute_map[row["ATTRIBUTE"]] = row["COUNT"]

    print("Loaded " + str(len(attributes_pd)) + " unique attributes")
    return attribute_map


class AttributeCleaner:
    def __init__(self):
        self.attribute_conversion_map = {}
        self.cleaned_attribute_map = {}

    @staticmethod
    def populate_conversion_map():
        attribute_conversion_map = {}
        attr_diff_pd = pd.read_csv(file_utils.unique_attributes_file_final_diff_all,
                                   header=None, encoding=file_utils.encoding)

        for index, row in attr_diff_pd.iterrows():  # todo remove nan
            for i, r in enumerate(row):
                if i != 0:
                    attribute_conversion_map[r] = row[0]

        return attribute_conversion_map

    @staticmethod
    def populate_cleaned_map():
        cleaned_attribute_map = {}
        attr_diff_pd = pd.read_csv(file_utils.unique_attributes_file_final_diff_all,
                                   header=None, encoding=file_utils.encoding)

        for index, row in attr_diff_pd.iterrows():  # todo remove nan
            cleaned_attribute_map[row[0]] = row[1:]

        return cleaned_attribute_map

    def get_clean_attribute(self, attribute: str) -> str:
        if len(self.populate_conversion_map) == 0:
            self.populate_conversion_map = AttributeCleaner.populate_conversion_map()

        if attribute in self.attribute_conversion_map:
            return str(self.attribute_conversion_map[attribute])
        else:
            print("Warning: attribute not in conversion map: " + attribute)
            return attribute

    def get_cleaned_attribute_list(self, attribute: str) -> str:
        if len(self.cleaned_attribute_map) == 0:
            self.cleaned_attribute_map = AttributeCleaner.populate_cleaned_map()

        return self.cleaned_attribute_map[attribute]
