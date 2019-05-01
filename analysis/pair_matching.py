import pandas as pd
from difflib import SequenceMatcher
from tqdm import tqdm
from multiprocessing import pool

from commons import file_utils


match_ratio = 0.85


def analyze():
    attributes = pd.read_csv(file_utils.unique_attributes_file_final, encoding=file_utils.encoding)
    columns = attributes["ATTRIBUTE"].tolist()
    find_similar_pairs_parallel(columns)


def find_similar_pairs(attribute_list):
    match_ratios = {}
    for i in tqdm(range(0, len(attribute_list))):
        for j in range(i + 1, len(attribute_list)):
            a1 = attribute_list[i][0]
            a2 = attribute_list[j][0]
            match_ratios[a1 + ", " + a2] = SequenceMatcher(None, a1, a2).ratio()

    sorted_match_ratios = sorted(match_ratios.items(), key=lambda kv: kv[1], reverse=True)
    print(sorted_match_ratios[:50])

    for x in sorted_match_ratios[:50]:
        print(str(x) + "\n")


def find_similar_pairs_parallel(attribute_list):
    matched_attributes = []
    job_list = []
    job_list_size = 1000
    p = pool.Pool(processes=8)
    for i in tqdm(range(0, len(attribute_list))):
        if (i + 1) % job_list_size == 0 or i == len(attribute_list) - 1:
            results = p.map(compare, job_list)
            for result in results:
                matched_attributes.extend(result)
            job_list = []
        else:
            job_list.append(attribute_list[i:])

    pd_matched_attributes = pd.DataFrame(matched_attributes)
    pd_matched_attributes = pd_matched_attributes.sort_values(by="RATIO", ascending=False)
    pd_matched_attributes.to_csv(file_utils.matched_attributes_file, index=False, encoding=file_utils.encoding)


def compare(attribute_list):
    matched_attributes = []
    for att in attribute_list[1:]:
        ratio = SequenceMatcher(None, attribute_list[0], att).ratio()
        if ratio >= match_ratio:
            matched_entry = {"ATTRIBUTE_1": attribute_list[0], "ATTRIBUTE_2": att, "RATIO": ratio}
            matched_attributes.append(matched_entry)

    return matched_attributes


if __name__ == "__main__":
    analyze()
