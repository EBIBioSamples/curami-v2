import pandas as pd
from sklearn.metrics import cohen_kappa_score

import neo4j_connector


def main():
    print("Calculating inter curator agreement")
    calculate_kappa()
    get_agreed_curations()


def calculate_kappa():
    # pd_manual_curations = neo4j_connector.get_manual_curations_all()
    # pd_manual_curations.to_csv("../../data/results/manual_curations.csv", index=False, encoding="utf-8")
    pd_manual_curations = pd.read_csv("../../data/results/manual_curations.csv")
    kappa_value = cohen_kappa_score(pd_manual_curations.iloc[:, 2], pd_manual_curations.iloc[:, 3])
    print("kappa between 2 curators = " + str(kappa_value))


def get_agreed_curations():
    agreed_curation_list = []
    pd_manual_curations = pd.read_csv("../../data/results/manual_curations.csv")
    for index, row in pd_manual_curations.iterrows():
        if row[2] == row[3]:
            agreed_curation_list.append({
                "ATTRIBUTE_1": row[0],
                "ATTRIBUTE_2": row[1],
                "CURATION": row[2]
            })

    pd_matched = pd.DataFrame(agreed_curation_list)
    pd_matched.to_csv("../../data/results/manual_curations_matched.csv", index=False)


if __name__ == "__main__":
    main()
