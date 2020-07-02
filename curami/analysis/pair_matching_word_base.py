import pandas as pd
from nltk.stem import LancasterStemmer, WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize

from curami.commons import file_utils

'''
Match pair of attributes for their base form similarity
Generates matched attribute file by measuring the syntactic similarity between the base form of the two attributes.
Outputs two attributes and similarity score
'''

match_ratio = 0.85


def analyze():
    attributes = pd.read_csv(file_utils.matched_attributes_file, encoding=file_utils.encoding)
    stemmer = LancasterStemmer()
    lemmatizer = WordNetLemmatizer()

    matched_attributes = []
    for index, row in attributes.iterrows():
        # lemmatize
        attribute1 = ' '.join(lemmatizer.lemmatize(w) for w in row["ATTRIBUTE_1"].split())
        attribute2 = ' '.join(lemmatizer.lemmatize(w) for w in row["ATTRIBUTE_2"].split())

        if attribute1 == attribute2:
            matched_attributes.append({"ATTRIBUTE_1": row["ATTRIBUTE_1"],
                                       "ATTRIBUTE_2": row["ATTRIBUTE_2"],
                                       "RATIO": 1})
            continue

        # stem
        attribute1 = ' '.join(stemmer.stem(w) for w in row["ATTRIBUTE_1"].split())
        attribute2 = ' '.join(stemmer.stem(w) for w in row["ATTRIBUTE_2"].split())

        if attribute1 == attribute2:
            matched_attributes.append({"ATTRIBUTE_1": row["ATTRIBUTE_1"],
                                       "ATTRIBUTE_2": row["ATTRIBUTE_2"],
                                       "RATIO": 0.8})

    pd_matched_attributes = pd.DataFrame(matched_attributes)
    pd_matched_attributes = pd_matched_attributes.sort_values(by="RATIO", ascending=False)
    pd_matched_attributes.to_csv(
        file_utils.word_base_matched_attribute_file, index=False, encoding=file_utils.encoding)


if __name__ == "__main__":
    analyze()
