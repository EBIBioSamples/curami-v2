import json
import sys
import seaborn as sns

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from commons import file_utils

sample_count_string = "total samples"
av_count_string = "total attributes"
unique_attribute_count_string = "unique attribute count"
unique_value_count_string = "unique value count"


def plot_correlation_heatmap():
    pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8")

    plt.figure(figsize=(20, 20))
    corr = pd_unique_attributes.corr()
    print(corr)
    fig = sns.heatmap(corr, square=True)
    fig.axes.set_title("Attribute Correlation", fontsize=20)
    plt.tick_params(labelsize=10)
    plt.savefig(file_utils.results_directory + "correlation_heatmap.png")
    plt.show()


def cluster():
    pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8")
    # pd_unique_attributes.replace(1.0, 1, inplace=True)
    # pd_unique_attributes.fillna(0, inplace=True)

    # pca = PCA(n_components=20).fit(pd_unique_attributes[0:100000])
    # pca_2d = pca.transform(pd_unique_attributes)

    print(pd_unique_attributes.describe())
    print(pd_unique_attributes.dtypes)

    kmeans = KMeans(n_clusters=10, random_state=0).fit(pd_unique_attributes)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    pd_kmeans = pd.DataFrame(labels)
    pd_unique_attributes.insert(pd_unique_attributes.shape[1], 'kmeans', pd_kmeans)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    scatter = ax.scatter(pd_unique_attributes['Organism'], pd_unique_attributes['sex'],
                         c=pd_kmeans[0], s=50)

    ax.set_title('K-Means Clustering')
    ax.set_xlabel('Organism')
    ax.set_ylabel('sex')
    plt.colorbar(scatter)

    plt.show()


def main(*args):
    # plot_correlation_heatmap()
    cluster()


if __name__ == "__main__":
    main(*sys.argv[1:])
