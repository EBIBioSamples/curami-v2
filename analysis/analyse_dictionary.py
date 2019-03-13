from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import commons.file_utils as file_utils
import commons.utils as curami_utils
import json


def test_count_vectorizer():
    vectorizer = CountVectorizer()
    corpus = {
        "This is the first document",
        "this is the second document",
        "This is the third doc"
    }
    x = vectorizer.fit_transform(corpus)
    # analyze = vectorizer.build_analyzer()
    print(vectorizer.get_feature_names())
    print(x)
    print(vectorizer.vocabulary_)


def test_feature_frequency():
    sample_list = file_utils.read_from_file(0)
    sample_string_list = []
    for sample in sample_list:
        sample_string_list.append(json.dumps(sample))

    vectorizer = CountVectorizer()
    x = vectorizer.fit_transform(sample_string_list)
    print(len(vectorizer.get_feature_names()))
    print(x.toarray())
    print(x.toarray().sum(axis=0))
    print(vectorizer.get_feature_names())

    # tf_transformer = TfidfTransformer(use_idf=False).fit(sample_string_list)
    # X_train_tf = tf_transformer.transform(X_train_counts)
    # X_train_tf.shape

    # tf_transformer = TfidfTransformer().fit_transform(x)
    # print(tf_transformer.shape)
    # print(tf_transformer)


def analyse_attributes():
    attributes_list = file_utils.get_all_attributes(1, 6)
    attribute_dic = {}
    for attributes in attributes_list:
        for attribute in attributes:
            if attribute in attribute_dic:
                attribute_dic[attribute] = attribute_dic[attribute] + 1
            else:
                attribute_dic[attribute] = 1

    sorted_attributes = sorted(attribute_dic.items(), key=lambda kv: kv[1], reverse=True)
    print(sorted_attributes)
    print(len(sorted_attributes))
    return sorted_attributes


def analyse_values():
    attributes_list = file_utils.get_all_values(1, 6)
    attribute_dic = {}
    for attributes in attributes_list:
        for attribute in attributes:
            if attribute in attribute_dic:
                attribute_dic[attribute] = attribute_dic[attribute] + 1
            else:
                attribute_dic[attribute] = 1

    sorted_attributes = sorted(attribute_dic.items(), key=lambda kv: kv[1], reverse=True)
    print(sorted_attributes[:50])
    print(len(sorted_attributes))
    return sorted_attributes


def find_case_differences(attributes):
    lowercase_attributes = {}
    for attribute in attributes:
        lowercase_attribute = attribute[0].lower()
        if lowercase_attribute in lowercase_attributes:
            lowercase_attributes[lowercase_attribute] = lowercase_attributes[lowercase_attribute] + 1
            print(lowercase_attribute)
        else:
            lowercase_attributes[lowercase_attribute] = 1

    return lowercase_attributes


def find_underscore_differences(attributes):
    modified_attributes = {}
    for attribute in attributes:
        modified_attribute = attribute[0].replace("_", " ")
        if modified_attribute in modified_attributes:
            modified_attributes[modified_attribute] = modified_attributes[modified_attribute] + 1
            print(modified_attribute)
        else:
            modified_attributes[modified_attribute] = 1

    return modified_attributes


# analyse_attributes()
# analyse_values()
find_case_differences(analyse_attributes())
# find_underscore_differences(analyse_attributes())
