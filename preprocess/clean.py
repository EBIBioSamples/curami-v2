import pandas as pd
import re
from difflib import SequenceMatcher
from tqdm import tqdm
from multiprocessing import pool

from commons import file_utils


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

space_after_parenthesis_re = re.compile(r'\( ')
space_before_parenthesis_re = re.compile(r' \)')
space_after_bracket_re = re.compile(r'\[ ')
space_before_bracket_re = re.compile(r' \]')
extra_spaces_re = re.compile(r'\s+')

leading_apostrophe_dash = re.compile(r'^[-\']')
dash_followed_by_underscore_re = re.compile(r'([-:=./])(_)')
space_around_slash = re.compile(r' / | /|/ ')


def preprocess():
    clean()


def clean():
    file_utils.create_data_directory()
    attribute_list = convert_attributes_to_simple_case()
    convert_attributes_snake_case()
    convert_attributes_remove_non_word_characters()
    # find_similar_pairs(attribute_list)
    # find_similar_pairs_parallel(attribute_list)


def camel_to_snake(attribute):
    attribute = first_cap_re.sub(r'\1_\2', attribute)
    attribute = all_cap_re.sub(r'\1_\2', attribute)
    return dash_followed_by_underscore_re.sub(r'\1', attribute).lower()


def remove_whitespace_in_parenthesis(attribute):
    attribute = space_after_parenthesis_re.sub("(", attribute)
    attribute = space_before_parenthesis_re.sub(")", attribute)
    attribute = space_after_bracket_re.sub("[", attribute)
    attribute = space_before_bracket_re.sub("]", attribute)
    return attribute


def remove_other_fancy_characters(attribute):
    attribute = leading_apostrophe_dash.sub("", attribute)
    attribute = dash_followed_by_underscore_re.sub("-", attribute)
    attribute = space_around_slash.sub("/", attribute)
    attribute = attribute.replace("_", " ")
    attribute = attribute.replace("\\", "/")
    attribute = extra_spaces_re.sub(" ", attribute)
    return attribute.lower().strip()


def convert_attributes_to_simple_case():
    # convert to simple case and remove underscore and trim
    print("converting to simple case")
    attributes = pd.read_csv(file_utils.unique_attributes_file, encoding="utf-8")
    simple_case_attributes = {}
    simple_case_attribute_list = {}
    for index, row in attributes.iterrows():
        # attribute = re.sub(r"\s+", " ", str(row["ATTRIBUTE"]).lower().replace("_", " ")).strip()
        attribute = remove_other_fancy_characters(str(row["ATTRIBUTE"]))
        attribute = remove_whitespace_in_parenthesis(attribute)
        if attribute in simple_case_attributes:
            simple_case_attributes[attribute] = simple_case_attributes[attribute] + row["COUNT"]
            simple_case_attribute_list[attribute].append(row["ATTRIBUTE"])
        else:
            simple_case_attributes[attribute] = row["COUNT"]
            simple_case_attribute_list[attribute] = [attribute, row["ATTRIBUTE"]]

    pd_unique_attributes = pd.DataFrame(
        list(sorted(simple_case_attributes.items(), key=lambda kv: kv[1], reverse=True)), columns=["ATTRIBUTE", "COUNT"])
    pd_unique_attributes.to_csv(file_utils.unique_values_file_simple, index=False, encoding=file_utils.encoding)

    x = [item for item in simple_case_attribute_list.values() if len(item) > 2]
    pd_case_matched_attributes = pd.DataFrame(x)
    pd_case_matched_attributes.to_csv(file_utils.unique_values_file_simple_diff, index=False, header=False, encoding=file_utils.encoding)

    return list(simple_case_attributes.keys())


def convert_attributes_snake_case():
    print("converting camel to snake case")
    attributes = pd.read_csv(file_utils.unique_attributes_file, encoding="utf-8")
    simple_case_attributes = {}
    simple_case_attribute_list = {}
    for index, row in attributes.iterrows():
        attribute = camel_to_snake(str(row["ATTRIBUTE"]))
        # attribute = re.sub(r"\s+", " ", attribute.lower().replace("_", " ")).strip()
        attribute = remove_other_fancy_characters(attribute)
        attribute = remove_whitespace_in_parenthesis(attribute)
        if attribute in simple_case_attributes:
            simple_case_attributes[attribute] = simple_case_attributes[attribute] + row["COUNT"]
            simple_case_attribute_list[attribute].append(row["ATTRIBUTE"])
        else:
            simple_case_attributes[attribute] = row["COUNT"]
            simple_case_attribute_list[attribute] = [attribute, row["ATTRIBUTE"]]

    pd_unique_attributes = pd.DataFrame(
        list(sorted(simple_case_attributes.items(), key=lambda kv: kv[1], reverse=True)), columns=["ATTRIBUTE", "COUNT"])
    pd_unique_attributes.to_csv(file_utils.unique_values_file_underscore, index=False, encoding="utf-8")

    x = [item for item in simple_case_attribute_list.values() if len(item) > 2]
    pd_case_matched_attributes = pd.DataFrame(x)
    pd_case_matched_attributes.to_csv(file_utils.unique_values_file_underscore_diff, index=False, header=False, encoding=file_utils.encoding)


def convert_attributes_remove_non_word_characters():
    print("removing all punctuations")
    attributes = pd.read_csv(file_utils.unique_values_file_simple, encoding="utf-8")
    simple_case_attributes = {}
    simple_case_attribute_list = {}
    for index, row in attributes.iterrows():
        attribute1 = str(row["ATTRIBUTE"]).strip()
        attribute = re.sub(r"[^\w]", " ", str(row["ATTRIBUTE"]))
        attribute = re.sub(r"\s+", " ", attribute.strip())
        # if attribute != attribute1:
        #     print(attribute1 + " -> " + attribute)

        if attribute in simple_case_attributes:
            simple_case_attributes[attribute] = simple_case_attributes[attribute] + row["COUNT"]
            simple_case_attribute_list[attribute].append(row["ATTRIBUTE"])
        else:
            simple_case_attributes[attribute] = row["COUNT"]
            simple_case_attribute_list[attribute] = [attribute, row["ATTRIBUTE"]]

    pd_unique_attributes = pd.DataFrame(
        list(sorted(simple_case_attributes.items(), key=lambda kv: kv[1], reverse=True)), columns=["ATTRIBUTE", "COUNT"])
    pd_unique_attributes.to_csv(file_utils.unique_values_file_non_word, index=False, encoding="utf-8")

    x = [item for item in simple_case_attribute_list.values() if len(item) > 2]
    pd_case_matched_attributes = pd.DataFrame(x)
    pd_case_matched_attributes.to_csv(file_utils.unique_values_file_non_word_diff, index=False, header=False, encoding=file_utils.encoding)


def compare_cleanup_process():
    pd_attr_1 = pd.read_csv(file_utils.unique_values_file_simple, encoding=file_utils.encoding)
    pd_attr_2 = pd.read_csv(file_utils.unique_values_file_underscore, encoding=file_utils.encoding)
    pd_attr_diff_1 = pd.read_csv(file_utils.unique_values_file_simple_diff, encoding=file_utils.encoding)
    pd_attr_diff_2 = pd.read_csv(file_utils.unique_values_file_underscore_diff, encoding=file_utils.encoding)

    attr1_set = set(pd_attr_1["ATTRIBUTE"])
    attr2_set = set(pd_attr_2["ATTRIBUTE"])

    attr1_diff_map = {}
    attr2_diff_map = {}
    for index, row in pd_attr_diff_1.iterrows():
        attr1_diff_map[row[0]] = [str(val) for val in row[1:] if str(val) != 'nan']
    for index, row in pd_attr_diff_2.iterrows():
        attr2_diff_map[row[0]] = [str(val) for val in row[1:] if str(val) != 'nan']

    attribute1_to_conversion_map = {}
    attribute2_to_conversion_map = {}
    for index, row in pd_attr_diff_1.iterrows():
        for i, r in enumerate(row):
            if i != 0:
                attribute1_to_conversion_map[r] = row[0]
    for index, row in pd_attr_diff_2.iterrows():
        for i, r in enumerate(row):
            if i != 0:
                attribute2_to_conversion_map[r] = row[0]

    # for val in attr1_set:
    #     if val not in attr2_set:
    #         if val in attr1_diff_map:
    #             original_att_set = attr1_diff_map[val]
    #             print(original_att_set)
    #             for original_att in original_att_set:
    #                 print(attribute1_to_conversion_map[original_att])

    for val in attr1_set:
        if val not in attr2_set:
            if val in attr1_diff_map:
                original_att = attr1_diff_map[val]
                print(original_att)
                if isinstance(original_att, list):
                    for l in original_att:
                        if l in attribute2_to_conversion_map:
                            print(attribute2_to_conversion_map[l])
                else:
                    print(attribute2_to_conversion_map[original_att])


    print("==========================================================")

    # for val in attr2_set:
    #     if val not in attr1_set:
    #         if val in attr2_diff_map:
    #             original_att_set = attr2_diff_map[val]
    #             print(original_att_set)
    #
    # for val in attr2_set:
    #     if val not in attr1_set:
    #         print(val)




    # for index1, row1 in pd_attr_1.iterrows():
    #     equal = False
    #     for index2, row2 in pd_attr_2.iterrows():
    #         if str(row1["ATTRIBUTE"]) == str(row2["ATTRIBUTE"]):
    #             equal = True
    #     if not equal:
    #         print(str(row1["ATTRIBUTE"]))


if __name__ == "__main__":
    # preprocess()
    compare_cleanup_process()


    # print(re.sub(r'^[-\']', '', "-Disease-de"))
    # print(re.sub(r'^[-\']', '', "-Disease-de"))
    # print(re.sub(r'^[-\']', '', "\'HELLNo-oi\'"))
    # print(re.sub(r'[^[\-\']', '', "\'HELLNo"))


    # first_cap_re = re.compile('(.)([A-Z][a-z]+)')
    # all_cap_re = re.compile('([a-z0-9])([A-Z])')
    #
    # def convert(name):
    #     s1 = first_cap_re.sub(r'\1_\2', name)
    #     return all_cap_re.sub(r'\1_\2', s1).lower()
    #
    #
    # remove_space = re.compile('')
    #
    # string_to_check = "geographic location ( latitude )"
    # print(re.sub("\( ", "(", string_to_check))
    # print(re.sub(" \)", ")", string_to_check))
    #
    # print(convert("geographic location (latitude),Geographic location (latitude),Geographic location (Latitude)"))
    # print(convert("geographic location (latitude))"))
    # print(convert("Geographic location (latitude)"))
    # print(convert("Geographic location (Latitude)"))
    # print(convert(" Pcr Primers"))
    # print(convert("hello_Worlld"))
    # print(convert("hello__Worlld"))
    # print(convert("hello_Worl_ld"))
    # print(convert("hello Worlld"))
    # print(convert("helloWor lld"))
    # print(convert("helloWorlld123"))
    # print(convert("helloW2or lld"))
    # print(convert("helloWWWor lld"))