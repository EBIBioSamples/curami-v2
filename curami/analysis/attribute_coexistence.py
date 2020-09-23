import json

import numpy as np
import pandas as pd

from curami.commons import file_utils


def analyze():
    calculate_coexistence_probability()


def calculate_coexistence_probability():
    print("Calculating coexistence probability")
    attribute_coexistence_count_pd = pd.read_csv(file_utils.coexistence_file_final, encoding=file_utils.encoding)
    attribute_coexistence_count_pd.columns = ["ATTRIBUTE_1", "ATTRIBUTE_2", "COEXISTENCE_COUNT"]
    attribute_count_pd = pd.read_csv(file_utils.unique_attributes_file_final, encoding=file_utils.encoding)
    with open(file_utils.summary_file, "r") as data_file:
        summary = json.load(data_file)

    attribute_count_pd["ATTRIBUTE_PROBABILITY"] = attribute_count_pd["COUNT"] / summary["total samples"]

    merge_df = pd.merge(left=attribute_coexistence_count_pd, right=attribute_count_pd,
                        left_on="ATTRIBUTE_1", right_on="ATTRIBUTE")
    merge_df.rename(columns={"COUNT": "ATTRIBUTE_1_COUNT",
                             "ATTRIBUTE_PROBABILITY": "ATTRIBUTE_1_PROBABILITY"}, inplace=True)
    del merge_df["ATTRIBUTE"]
    merge_df = pd.merge(left=merge_df, right=attribute_count_pd,
                        left_on="ATTRIBUTE_2", right_on="ATTRIBUTE")
    merge_df.rename(columns={"COUNT": "ATTRIBUTE_2_COUNT",
                             "ATTRIBUTE_PROBABILITY": "ATTRIBUTE_2_PROBABILITY"}, inplace=True)
    del merge_df["ATTRIBUTE"]

    merge_df["EXPECTED_COEXISTENCE"] = \
        merge_df["ATTRIBUTE_1_PROBABILITY"] * merge_df["ATTRIBUTE_2_PROBABILITY"] * summary["total samples"]
    merge_df["DIFF_COEXISTENCE"] = merge_df["COEXISTENCE_COUNT"] - merge_df["EXPECTED_COEXISTENCE"]
    merge_df["DIFF_WEIGHT"] = merge_df["DIFF_COEXISTENCE"] / merge_df["DIFF_COEXISTENCE"].sum()

    # phi-coefficient = (N * N12 - N1 * N2) / (N1 * N2 * (N - N1) * (N - N2)) ^ 1/2
    # N = total samples, N12 = coexistence count, N1 = attribute 1 count, N2 = attribute 2 count
    merge_df["PHI_COEFFICIENT"] = (summary["total samples"] * merge_df["COEXISTENCE_COUNT"] -
                                   merge_df["ATTRIBUTE_1_COUNT"] * merge_df["ATTRIBUTE_2_COUNT"]) / \
                                  np.sqrt((merge_df["ATTRIBUTE_1_COUNT"] * merge_df["ATTRIBUTE_2_COUNT"] *
                                           (summary["total samples"] - merge_df["ATTRIBUTE_2_COUNT"]) *
                                           (summary["total samples"] - merge_df["ATTRIBUTE_2_COUNT"])))

    merge_df["DIFF_COEXISTENCE_ABS"] = abs(merge_df["DIFF_COEXISTENCE"])

    merge_df.sort_values(by=['COEXISTENCE_COUNT'], inplace=True, ascending=False)
    merge_df.to_csv(file_utils.coexistence_probability_file, index=False, encoding=file_utils.encoding)


if __name__ == "__main__":
    analyze()
