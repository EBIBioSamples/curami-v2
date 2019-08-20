import pandas as pd

from curami.commons import file_utils
from curami.commons.word_processor import WordProcessor


class AttributeCleaner:
    def __init__(self):
        self.attribute_conversion_map = self.populate_conversion_map()

    def populate_conversion_map(self):
        attribute_conversion_map = {}
        attr_diff_pd = pd.read_csv(file_utils.unique_attributes_file_final_diff_all,
                                   header=None, encoding=file_utils.encoding)

        for index, row in attr_diff_pd.iterrows():  # todo remove nan
            for i, r in enumerate(row):
                if i != 0:
                    attribute_conversion_map[r] = row[0]

        return attribute_conversion_map

    def get_clean_attribute(self, attribute):
        if attribute in self.attribute_conversion_map:
            return str(self.attribute_conversion_map[attribute])
        else:
            print("Warning: attribute not in conversion map: " + attribute)
            return attribute


def preprocess():
    file_utils.create_data_directory()
    clean_attributes(True)  # camel case conversion
    clean_attributes(False)  # without camel case conversion
    merge_clean_processes()  # compare two and select best results
    recalculate_coexistence_matrix()  # recalculate coexistence with cleaned attributes


def clean_attributes(do_camel_to_snake_conversion):
    # convert to simple case and remove underscore and trim
    print("Attribute cleaning, camel_conversion = " + str(do_camel_to_snake_conversion))
    attributes = pd.read_csv(file_utils.unique_attributes_file, encoding="utf-8")
    simple_case_attributes = {}
    simple_case_attribute_list = {}
    word_processor = WordProcessor()
    for index, row in attributes.iterrows():
        attribute = word_processor.cleanup_string(str(row["ATTRIBUTE"]), do_camel_to_snake_conversion)
        if attribute in simple_case_attributes:
            simple_case_attributes[attribute] = simple_case_attributes[attribute] + row["COUNT"]
            simple_case_attribute_list[attribute].append(row["ATTRIBUTE"])
        else:
            simple_case_attributes[attribute] = row["COUNT"]
            simple_case_attribute_list[attribute] = [attribute, row["ATTRIBUTE"]]

    pd_unique_attributes = pd.DataFrame(
        list(sorted(simple_case_attributes.items(), key=lambda kv: kv[1], reverse=True)),
        columns=["ATTRIBUTE", "COUNT"])
    pd_unique_attributes.to_csv(file_utils.unique_attributes_file_final + '.camel=' + str(do_camel_to_snake_conversion)
                                , index=False, encoding=file_utils.encoding)

    x = [item for item in simple_case_attribute_list.values() if len(item) > 2]
    pd_case_matched_attributes = pd.DataFrame(x)
    pd_case_matched_attributes.to_csv(
        file_utils.unique_attributes_file_final_diff + '.camel=' + str(do_camel_to_snake_conversion),
        index=False, header=False, encoding=file_utils.encoding)

    x = [item for item in simple_case_attribute_list.values() if len(item) > 1]
    pd_case_matched_attributes_all = pd.DataFrame(x)
    pd_case_matched_attributes_all.to_csv(
        file_utils.unique_attributes_file_final_diff_all + '.camel=' + str(do_camel_to_snake_conversion),
        index=False, header=False, encoding=file_utils.encoding)

    return list(simple_case_attributes.keys())


def merge_clean_processes():
    # todo this method is too complicated, need to make it less complicated
    # Compare between two preprocessed set of attributes and select best attributes.
    # 1. If there are common attributes select them
    # 2. If there are dissimilar attributes select them based on dictionary or existence

    print('loading data and preparing data structures')
    pd_attr_1 = pd.read_csv(file_utils.unique_attributes_file_final + '.camel=False', encoding=file_utils.encoding)
    pd_attr_2 = pd.read_csv(file_utils.unique_attributes_file_final + '.camel=True', encoding=file_utils.encoding)
    pd_attr_diff_1 = pd.read_csv(file_utils.unique_attributes_file_final_diff_all + '.camel=False', header=None,
                                 encoding=file_utils.encoding)
    pd_attr_diff_2 = pd.read_csv(file_utils.unique_attributes_file_final_diff_all + '.camel=True', header=None,
                                 encoding=file_utils.encoding)

    attr1_set = set(pd_attr_1["ATTRIBUTE"])
    attr2_set = set(pd_attr_2["ATTRIBUTE"])

    # create data structures to make processing easier
    attr1_diff_map = {}
    attr2_diff_map = {}
    for index, row in pd_attr_diff_1.iterrows():
        attr1_diff_map[row[0]] = [str(val) for val in row[1:] if str(val) != 'nan']
    for index, row in pd_attr_diff_2.iterrows():
        attr2_diff_map[row[0]] = [str(val) for val in row[1:] if str(val) != 'nan']

    attribute1_to_conversion_map = {}
    attribute2_to_conversion_map = {}
    for index, row in pd_attr_diff_1.iterrows():  # todo remove nan
        for i, r in enumerate(row):
            if i != 0 and r != '' and r == r:  # nan check x == x
                attribute1_to_conversion_map[r] = row[0]
    for index, row in pd_attr_diff_2.iterrows():
        for i, r in enumerate(row):
            if i != 0 and r != '' and r == r:  # nan check x == x
                attribute2_to_conversion_map[r] = row[0]

    print('Comparing attributes')
    set_intersection = attr1_set.intersection(attr2_set)
    set_difference = attr1_set.difference(attr2_set)

    clean_attributes_conversions = {}
    clean_attribute_set = attr1_set.intersection(attr2_set)
    print("Number of matched attributes in both sets: " + str(len(clean_attribute_set)))

    # put common attributes in the both set to final list
    for attribute in clean_attribute_set:
        original_attribute_set1 = attr1_diff_map[attribute]
        original_attribute_set2 = attr2_diff_map[attribute]
        original_attributes = set(original_attribute_set1).union(set(original_attribute_set2))
        clean_attributes_conversions[attribute] = original_attributes

    # get attributes in one set and not in other, create map with key=original attribute
    reconcile_map = {}
    for val in attr1_set:
        if val not in attr2_set:
            original_att_set = attr1_diff_map[val]
            for original_att in original_att_set:
                reconcile_map[original_att] = [val]
                # print(val + " : " + str(original_att_set) + " : " + attribute2_to_conversion_map[original_att])

    for val in attr2_set:
        if val not in attr1_set:
            original_att_set = attr2_diff_map[val]
            for original_att in original_att_set:
                if original_att in reconcile_map:
                    reconcile_map[original_att].append(val)
                else:
                    reconcile_map[original_att] = [val]
                # print(val + " : " + str(original_att_set) + " : " + attribute1_to_conversion_map[original_att])

    # If len=1 then value is only present in one attribute set.
    # That mean it has converged with different attribute in other set
    # If len=2 this attribute has no converged values, select either of the attributes based on a dictionary test
    for key, val in reconcile_map.items():
        if len(val) == 1:
            first_value = attribute1_to_conversion_map[key]
            second_value = attribute2_to_conversion_map[key]
            if first_value == val[0]:
                print("Second value is already in the set: original = " + key +
                      ", first = " + first_value + " , second[y] = " + second_value)
                clean_attribute_set.add(second_value)
                if second_value in clean_attributes_conversions:
                    clean_attributes_conversions[second_value].add(key)
                else:
                    clean_attributes_conversions[second_value] = {key}
            if second_value == val[0]:
                print("First value is already in the set: original = " + key +
                      ", first[y] = " + first_value + " , second = " + second_value)
                clean_attribute_set.add(first_value)
                if first_value in clean_attributes_conversions:
                    clean_attributes_conversions[first_value].add(key)
                else:
                    clean_attributes_conversions[first_value] = {key}
        if len(val) == 2:
            select_first = WordProcessor.dictionary_check(val[0])
            select_second = WordProcessor.dictionary_check(val[1])

            if select_first and select_second:
                print("Both phrases matched with the dictionary: " + key + ", " + str(val))
                clean_attribute_set.add(key)
                if key in clean_attributes_conversions:
                    clean_attributes_conversions[key].add(key)
                else:
                    clean_attributes_conversions[key] = {key}
            elif select_first:
                print("First selected: " + key + ", " + str(val))
                clean_attribute_set.add(val[0])
                if val[0] in clean_attributes_conversions:
                    clean_attributes_conversions[val[0]].add(key)
                else:
                    clean_attributes_conversions[val[0]] = {key}
            elif select_second:
                print("Second selected: " + key + ", " + str(val))
                clean_attribute_set.add(val[1])
                if val[1] in clean_attributes_conversions:
                    clean_attributes_conversions[val[1]].add(key)
                else:
                    clean_attributes_conversions[val[1]] = {key}
            else:
                print("No dictionary match, adding original value: " + key + ", " + str(val))
                clean_attribute_set.add(key)
                if key in clean_attributes_conversions:
                    clean_attributes_conversions[key].add(key)
                else:
                    clean_attributes_conversions[key] = {key}

    attribute_frequency_pd = pd.read_csv(file_utils.unique_attributes_file, encoding=file_utils.encoding)
    attribute_frequency_map = {}
    for index, row in attribute_frequency_pd.iterrows():
        attribute_frequency_map[row["ATTRIBUTE"]] = row["COUNT"]

    clean_attributes = {}

    for attribute in clean_attribute_set:
        for original_attribute in clean_attributes_conversions[attribute]:
            if attribute in clean_attributes:
                clean_attributes[attribute] = clean_attributes[attribute] + attribute_frequency_map[original_attribute]
            else:
                clean_attributes[attribute] = attribute_frequency_map[original_attribute]

    print('persisting to file system')
    pd_unique_attributes = pd.DataFrame(
        list(sorted(clean_attributes.items(), key=lambda kv: kv[1], reverse=True)),
        columns=["ATTRIBUTE", "COUNT"])
    pd_unique_attributes.to_csv(file_utils.unique_attributes_file_final, index=False, encoding=file_utils.encoding)

    clean_attributes_conversions_list = []
    for key, value in clean_attributes_conversions.items():
        single_attribute_list = [key]
        for item in value:
            single_attribute_list.append(item)
        clean_attributes_conversions_list.append(single_attribute_list)

    x = [item for item in clean_attributes_conversions_list if len(item) > 2]
    pd_case_matched_attributes_all = pd.DataFrame(x)
    pd_case_matched_attributes_all.to_csv(file_utils.unique_attributes_file_final_diff, index=False, header=False,
                                          encoding=file_utils.encoding)

    pd_case_matched_attributes = pd.DataFrame(clean_attributes_conversions_list)
    pd_case_matched_attributes.to_csv(file_utils.unique_attributes_file_final_diff_all, index=False, header=False,
                                      encoding=file_utils.encoding)


# calculate coexistence again for the cleaned attributes
def recalculate_coexistence_matrix():
    coexistence_map = {}
    coexistence_original_pd = pd.read_csv(file_utils.coexistence_file, encoding=file_utils.encoding)
    attribute_cleaner = AttributeCleaner()
    for index, row in coexistence_original_pd.iterrows():
        attribute1 = attribute_cleaner.get_clean_attribute(row[0])
        attribute2 = attribute_cleaner.get_clean_attribute(row[1])
        count = int(row[2])

        if attribute1 > attribute2:
            temp = attribute1
            attribute1 = attribute2
            attribute2 = temp

        combined_key = attribute1 + "~" + attribute2
        if combined_key not in coexistence_map:
            coexistence_map[combined_key] = {"ATTRIBUTE_1": attribute1, "ATTRIBUTE_2": attribute2, "COUNT": count}
        else:
            coexistence_map[combined_key]["COUNT"] = coexistence_map[combined_key]["COUNT"] + count

    print("Writing to filesystem")
    pd_unique_attributes = pd.DataFrame(
        list(sorted(coexistence_map.values(), key=lambda kv: kv["COUNT"], reverse=True)),
        columns=["ATTRIBUTE_1", "ATTRIBUTE_2", "COUNT"])
    pd_unique_attributes.to_csv(file_utils.coexistence_file_final, index=False, encoding="utf-8")


if __name__ == "__main__":
    preprocess()

