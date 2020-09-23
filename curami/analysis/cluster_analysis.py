import sys
import seaborn as sns

import prince
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.cluster.hierarchy as sch
from sklearn.cluster import KMeans, DBSCAN, Birch, MeanShift, \
    SpectralClustering, AffinityPropagation, FeatureAgglomeration, AgglomerativeClustering
from sklearn.decomposition import PCA, KernelPCA, LatentDirichletAllocation, NMF, \
    IncrementalPCA, SparsePCA, TruncatedSVD, MiniBatchDictionaryLearning, FastICA
from sklearn.random_projection import GaussianRandomProjection, SparseRandomProjection
from sklearn.manifold import MDS, Isomap, TSNE, LocallyLinearEmbedding
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis


import plotly.express as px

from curami.commons import file_utils

sample_count_string = "total samples"
av_count_string = "total attributes"
unique_attribute_count_string = "unique attribute count"
unique_value_count_string = "unique value count"

cluster_label = 4


def get_cluster_attribute_count():
    print("getting cluster attribute count")
    clustered_samples = pd.read_csv(file_utils.clustered_samples_file, encoding=file_utils.encoding)

    samples_cluster = clustered_samples.loc[clustered_samples['cluster_labels'] == cluster_label]
    attribute_sum = samples_cluster.sum()
    # attribute_sum.sort_values(axis=0, inplace=True)
    # print(attribute_sum)

    attribute_sum_df = pd.DataFrame(data=attribute_sum, columns=["count"])
    attribute_sum_df['attribute'] = attribute_sum_df.index

    attribute_sum_df.drop(labels=['accession', 'cluster_labels'], inplace=True)
    attribute_sum_df = attribute_sum_df.reset_index(drop=True)

    attribute_sum_df.sort_values("count", ascending=False, inplace=True)
    print(len(samples_cluster))
    print(attribute_sum_df.head(30))


def main(*args):
    get_cluster_attribute_count()

if __name__ == "__main__":
    main(*sys.argv[1:])
