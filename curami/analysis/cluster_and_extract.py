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
from plotly.offline import plot

from curami.commons import file_utils

sample_count_string = "total samples"
av_count_string = "total attributes"
unique_attribute_count_string = "unique attribute count"
unique_value_count_string = "unique value count"


def main(*args):
    extract_cluster_plot()


def extract_cluster_plot():
    print("Cluster and extract features")
    # select features and build a dataset with selected features
    # cluster and assign labels
    # fore each label extract important features features: features can be ordered according to importance ?
    # Use classification algorithm to classify samples into labels


if __name__ == "__main__":
    main(*sys.argv[1:])
