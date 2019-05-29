import pandas as pd
import re
from nltk.corpus import words

from src.commons import file_utils


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
double_quotes_re = re.compile(r'(\"+)(.+?)(\"+)')


def preprocess():
    clean()


def clean():
    file_utils.create_data_directory()
    convert_attributes_to_simple_case()
    convert_attributes_snake_case()
    convert_attributes_remove_non_word_characters()


def camel_to_snake(original_attribute):
    attribute = original_attribute
    attribute = first_cap_re.sub(r'\1_\2', attribute)
    attribute = all_cap_re.sub(r'\1_\2', attribute)
    attribute = dash_followed_by_underscore_re.sub(r'\1', attribute)
    if not words_more_than_two_characters(attribute):
        attribute = original_attribute

    return attribute.lower()


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
    attribute = attribute.replace("\"", "")
    attribute = attribute.replace("_", " ")
    attribute = attribute.replace("\\", "/")
    attribute = extra_spaces_re.sub(" ", attribute)
    return attribute.lower().strip()


def words_more_than_two_characters(phrase):
    phrase = phrase.replace("_", " ")
    word_list = phrase.split()
    for word in word_list:
        if len(word) < 3 and word.lower() != "id":
            return False
    return True


def dictionary_check(phrase):
    word_list = phrase.split()
    for word in word_list:
        if word not in words.words():
            return False
    return True


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
    pd_unique_attributes.to_csv(file_utils.unique_attributes_file_simple, index=False, encoding=file_utils.encoding)

    x = [item for item in simple_case_attribute_list.values() if len(item) > 2]
    pd_case_matched_attributes = pd.DataFrame(x)
    pd_case_matched_attributes.to_csv(file_utils.unique_attributes_file_simple_diff, index=False, header=False, encoding=file_utils.encoding)

    x = [item for item in simple_case_attribute_list.values() if len(item) > 1]
    pd_case_matched_attributes_all = pd.DataFrame(x)
    pd_case_matched_attributes_all.to_csv(file_utils.unique_attributes_file_simple_diff_all, index=False, header=False, encoding=file_utils.encoding)

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
    pd_unique_attributes.to_csv(file_utils.unique_attributes_file_underscore, index=False, encoding="utf-8")

    x = [item for item in simple_case_attribute_list.values() if len(item) > 2]
    pd_case_matched_attributes = pd.DataFrame(x)
    pd_case_matched_attributes.to_csv(file_utils.unique_attributes_file_underscore_diff, index=False, header=False, encoding=file_utils.encoding)

    x = [item for item in simple_case_attribute_list.values() if len(item) > 1]
    pd_case_matched_attributes_all = pd.DataFrame(x)
    pd_case_matched_attributes_all.to_csv(file_utils.unique_attributes_file_underscore_diff_all, index=False, header=False, encoding=file_utils.encoding)


def convert_attributes_remove_non_word_characters():
    print("removing all punctuations")
    attributes = pd.read_csv(file_utils.unique_attributes_file_simple, encoding="utf-8")
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
    pd_unique_attributes.to_csv(file_utils.unique_attributes_file_non_word, index=False, encoding="utf-8")

    x = [item for item in simple_case_attribute_list.values() if len(item) > 2]
    pd_case_matched_attributes = pd.DataFrame(x)
    pd_case_matched_attributes.to_csv(file_utils.unique_attributes_file_non_word_diff, index=False, header=False, encoding=file_utils.encoding)


def compare_cleanup_process():
    pd_attr_1 = pd.read_csv(file_utils.unique_attributes_file_simple, encoding=file_utils.encoding)
    pd_attr_2 = pd.read_csv(file_utils.unique_attributes_file_underscore, encoding=file_utils.encoding)
    pd_attr_diff_1 = pd.read_csv(file_utils.unique_attributes_file_simple_diff_all, header=None, encoding=file_utils.encoding)
    pd_attr_diff_2 = pd.read_csv(file_utils.unique_attributes_file_underscore_diff_all, header=None, encoding=file_utils.encoding)

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

    set_intersection = attr1_set.intersection(attr2_set)
    set_difference = attr1_set.difference(attr2_set)

    clean_attributes_conversions = {}
    clean_attribute_set = attr1_set.intersection(attr2_set)

    for attribute in clean_attribute_set:
        original_attribute_set1 = attr1_diff_map[attribute]
        original_attribute_set2 = attr2_diff_map[attribute]
        original_attributes = set(original_attribute_set1).union(set(original_attribute_set2))
        clean_attributes_conversions[attribute] = original_attributes

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

    for key, val in reconcile_map.items():
        if len(val) == 1:
            first_value = attribute1_to_conversion_map[key]
            second_value = attribute2_to_conversion_map[key]
            if first_value == val[0]:
                print("first value get second: " + first_value + " X " + key + " Y " + second_value)
                clean_attribute_set.add(second_value)
                if second_value in clean_attributes_conversions:
                    clean_attributes_conversions[second_value].add(key)
                else:
                    clean_attributes_conversions[second_value] = {key}
            if second_value == val[0]:
                print("second value get first: " + second_value + " X " + key + " Y " + first_value)
                clean_attribute_set.add(first_value)
                if first_value in clean_attributes_conversions:
                    clean_attributes_conversions[first_value].add(key)
                else:
                    clean_attributes_conversions[first_value] = {key}
        if len(val) == 2:
            select_first = dictionary_check(val[0])
            select_second = dictionary_check(val[1])

            if select_first and select_second:
                print("impossible: " + str(val))
            elif select_first:
                print("first value: " + str(val))
                clean_attribute_set.add(val[0])
                if val[0] in clean_attributes_conversions:
                    clean_attributes_conversions[val[0]].add(key)
                else:
                    clean_attributes_conversions[val[0]] = {key}
            elif select_second:
                print("second value: " + str(val))
                clean_attribute_set.add(val[1])
                if val[1] in clean_attributes_conversions:
                    clean_attributes_conversions[val[1]].add(key)
                else:
                    clean_attributes_conversions[val[1]] = {key}
            else:
                print("cant help with: " + str(val))
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



if __name__ == "__main__":
    preprocess()
    compare_cleanup_process()
    # value = "\"\"\"hello\"\"\""
    # print("hello")
    # print(value)
    # print(re.compile(r'(\"+)(.+?)(\"+)').sub(r'\2', value))
    # print(re.sub(r'"""', "", value))

    # attribute_frequency_pd = pd.read_csv(file_utils.unique_attributes_file, encoding=file_utils.encoding)
    # attribute_frequency_map = {}
    # for index, row in attribute_frequency_pd.iterrows():
    #     attribute_frequency_map[row["ATTRIBUTE"]] = row["COUNT"]
    # print(attribute_frequency_map["organism"])

    # print("treatment" in words.words())
    # print("id" in words.words())
    # print("pub" in words.words())
    # print("med" in words.words())

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