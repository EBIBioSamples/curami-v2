import pandas as pd

import spell
from curami.commons import file_utils

# find spelling mistakes of identified similar pairs in previous step
match_ratio = 0.85


def analyze():
    attributes = pd.read_csv(file_utils.matched_attributes_file, encoding=file_utils.encoding)

    matched_attributes = []
    for index, row in attributes.iterrows():
        attribute1 = row["ATTRIBUTE_1"].split()
        attribute2 = row["ATTRIBUTE_2"].split()

        attribute1_correct_spelling = True
        attribute2_correct_spelling = True
        for w in attribute1:
            if not spell.spell_check(w):
                attribute1_correct_spelling = False
        for w in attribute2:
            if not spell.spell_check(w):
                attribute2_correct_spelling = False

        if attribute1_correct_spelling and not attribute2_correct_spelling:
            matched_attributes.append({"DICTIONARY_MATCHED": row["ATTRIBUTE_1"],
                                       "NOT_MATCHED": row["ATTRIBUTE_2"],
                                       "RATIO": row["RATIO"]})
            print(row["ATTRIBUTE_1"] + " : " + row["ATTRIBUTE_2"])

        if not attribute1_correct_spelling and attribute2_correct_spelling:
            matched_attributes.append({"DICTIONARY_MATCHED": row["ATTRIBUTE_2"],
                                       "NOT_MATCHED": row["ATTRIBUTE_1"],
                                       "RATIO": row["RATIO"]})

    pd_matched_attributes = pd.DataFrame(matched_attributes)
    pd_matched_attributes = pd_matched_attributes.sort_values(by="RATIO", ascending=False)
    pd_matched_attributes.to_csv(
        file_utils.dictionary_matched_attribute_file, index=False, encoding=file_utils.encoding)


if __name__ == "__main__":
    analyze()
