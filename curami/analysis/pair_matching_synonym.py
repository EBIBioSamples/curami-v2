from itertools import product
from multiprocessing import pool

import pandas as pd
from nltk.corpus import wordnet
from tqdm import tqdm

from curami.commons import file_utils

'''
Match pair of attributes for their similarity
Generates matched attribute file by measuring the semantic similarity between two attributes.
Outputs two attributes and similarity score
'''

match_ratio = 0.75


def analyze():
    attributes = pd.read_csv(file_utils.unique_attributes_file_final, encoding=file_utils.encoding)
    columns = attributes["ATTRIBUTE"].tolist()
    synsets_list = get_synsets(columns)
    # find_similar_pairs_parallel(synsets_list)
    find_similar_pairs(synsets_list)


def get_synsets(attribute_list):
    synsets_list = []
    for attribute in attribute_list:
        if not (' ' in str(attribute)):
            ss = wordnet.synsets(str(attribute))
            if len(ss):
                synsets_list.append({'attribute': str(attribute), 'synsets': set(s for s in ss)})

    return synsets_list


def find_similar_pairs(synsets_list):
    matched_attributes = []
    for i in tqdm(range(0, len(synsets_list))):
        for j in range(i + 1, len(synsets_list)):
            allsyns1 = synsets_list[i]['synsets']
            allsyns2 = synsets_list[j]['synsets']
            best = max((wordnet.wup_similarity(s1, s2) or 0, s1, s2) for s1, s2 in product(allsyns1, allsyns2))
            ratio = best[0]
            if ratio >= match_ratio:
                matched_entry = {"ATTRIBUTE_1": synsets_list[i]['attribute'],
                                 "ATTRIBUTE_2": synsets_list[j]['attribute'],
                                 "RATIO": ratio}
                matched_attributes.append(matched_entry)

    pd_matched_attributes = pd.DataFrame(matched_attributes)
    pd_matched_attributes = pd_matched_attributes.sort_values(by="RATIO", ascending=False)
    pd_matched_attributes.to_csv(file_utils.matched_synonym_attributes_file, index=False, encoding=file_utils.encoding)


def find_similar_pairs_parallel(synsets_list):
    matched_attributes = []
    job_list = []
    job_list_size = 8
    p = pool.Pool(processes=8)
    for i in tqdm(range(0, len(synsets_list))):
        if (i + 1) % job_list_size == 0 or i == len(synsets_list) - 1:
            results = p.map(compare, job_list)
            for result in results:
                matched_attributes.extend(result)
            job_list = []
        else:
            job_list.append(synsets_list[i:])

    pd_matched_attributes = pd.DataFrame(matched_attributes)
    pd_matched_attributes = pd_matched_attributes.sort_values(by="RATIO", ascending=False)
    pd_matched_attributes.to_csv(file_utils.matched_synonym_attributes_file, index=False, encoding=file_utils.encoding)


def compare(synsets_list):
    matched_attributes = []
    allsyns1 = synsets_list[0]['synsets']
    for s in synsets_list[1:]:
        allsyns2 = s['synsets']
        best = max((wordnet.wup_similarity(s1, s2) or 0, s1, s2) for s1, s2 in product(allsyns1, allsyns2))
        ratio = best[0]
        if ratio >= match_ratio:
            matched_entry = {"ATTRIBUTE_1": synsets_list[0]['attribute'], "ATTRIBUTE_2": s['attribute'], "RATIO": ratio}
            matched_attributes.append(matched_entry)

    return matched_attributes


if __name__ == "__main__":
    # analyze()
    ss = wordnet.synsets(str('human'))
    print(ss)
    ss = wordnet.synsets(str('host'))
    print(ss)
