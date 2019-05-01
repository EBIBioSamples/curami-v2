import json
import sys

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

from commons import file_utils

# Principal component analysis(PCA) ,
# Independent component analysis (ICA) ,
# Singular Value Decomposition (SVD) ,
# LDA(Latent Discriminent Analysis)

sample_count_string = "total samples"
av_count_string = "total attributes"
unique_attribute_count_string = "unique attribute count"
unique_value_count_string = "unique value count"


def cluster():
    pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8")
    kmeans = KMeans(n_clusters=10, random_state=0).fit(pd_unique_attributes)
    print(kmeans.labels_)

def draw_summary():
    print("Generating summary graphs...")
    # draw AV pair count per document vs document count
    # draw most frequent attributes and its counts
    # draw most frequent values and its counts
    # draw most frequent attribute value pairs and its counts

    pd_unique_attributes = pd.read_csv(file_utils.unique_attributes_file, encoding="utf-8")
    pd_unique_attributes.set_index("ATTRIBUTE", drop=True, inplace=True)
    pd_unique_attributes.head(50).plot.bar()

    pd_unique_attributes_clean = pd.read_csv(file_utils.unique_attributes_file_final, encoding="utf-8")
    pd_unique_attributes_clean.set_index("ATTRIBUTE", drop=True, inplace=True)
    pd_unique_attributes_clean.head(50).plot.bar()

    pd_unique_values = pd.read_csv(file_utils.unique_values_file, encoding="utf-8")
    # pd_unique_values.set_index("VALUE", drop=True, inplace=True)
    pd_unique_values.head(50).plot()
    plt.show()


def main(*args):
    cluster()


if __name__ == "__main__":
    main(*sys.argv[1:])
