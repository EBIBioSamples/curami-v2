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
    # plot_correlation_heatmap()
    # cluster()
    # clustering_dbscan()
    # pca_plot_test()
    # mca_plot_test()
    # extract_plot_test()
    extract_cluster_plot()
    # hierarchical_clustering()


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


def clustering_kmeans():
    pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8")
    # pd_unique_attributes.replace(1.0, 1, inplace=True)
    # pd_unique_attributes.fillna(0, inplace=True)

    # pca = PCA(n_components=20).fit(pd_unique_attributes[0:100000])
    # pca_2d = pca.transform(pd_unique_attributes)

    print(pd_unique_attributes.describe())
    print(pd_unique_attributes.dtypes)

    del pd_unique_attributes['accession']

    kmeans = KMeans(n_clusters=10, random_state=0).fit(pd_unique_attributes)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    pd_kmeans = pd.DataFrame(labels)
    pd_unique_attributes.insert(pd_unique_attributes.shape[1], 'kmeans', pd_kmeans)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    scatter = ax.scatter(pd_unique_attributes['organism'], pd_unique_attributes['sex'],
                         c=pd_kmeans[0], s=50)

    ax.set_title('K-Means Clustering')
    ax.set_xlabel('organism')
    ax.set_ylabel('sex')
    plt.colorbar(scatter)

    plt.show()


def clustering_dbscan():

    pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8").sample(50000)

    print(pd_unique_attributes.describe())
    print(pd_unique_attributes.dtypes)

    accessions = pd_unique_attributes['accession']
    del pd_unique_attributes['accession']

    dbscan = DBSCAN(eps=0.3, min_samples=1000, metric='euclidean')
    dbscan.fit(pd_unique_attributes)

    labels = dbscan.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)
    print(labels)
    print("no of clusters: %d" % n_clusters_)
    print("noise points: %d" % n_noise_)

    pca = PCA(n_components=2)
    pca_2d = pca.fit_transform(pd_unique_attributes)

    plt.scatter(pca_2d[:, 0], pca_2d[:, 1], c=(labels + 2) / 20)

    plt.show()


def pca_plot_test():
    pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8")

    print(pd_unique_attributes.describe())
    print(pd_unique_attributes.dtypes)

    accessions = pd_unique_attributes['accession']
    del pd_unique_attributes['accession']

    pca = PCA(n_components=3)
    pca_2d = pca.fit_transform(pd_unique_attributes)

    fig = plt.figure()
    ax = fig.add_subplot(221, projection='3d')
    ax.scatter(pca_2d[:, 0], pca_2d[:, 1],  pca_2d[:, 2])

    ax = fig.add_subplot(222)
    ax.scatter(pca_2d[:, 0], pca_2d[:, 1])

    ax = fig.add_subplot(223)
    ax.scatter(pca_2d[:, 0], pca_2d[:, 2])

    ax = fig.add_subplot(224)
    ax.scatter(pca_2d[:, 1], pca_2d[:, 2])

    plt.show()


def mca_plot_test():
    pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8")

    print(pd_unique_attributes.describe())
    print(pd_unique_attributes.dtypes)

    accessions = pd_unique_attributes['accession']
    del pd_unique_attributes['accession']

    mca = prince.MCA(n_components=3).fit(pd_unique_attributes)
    mca_2d = mca.transform(pd_unique_attributes)

    fig = plt.figure()
    ax = fig.add_subplot(221, projection='3d')
    ax.scatter(mca_2d[0], mca_2d[1],  mca_2d[2])

    ax1 = fig.add_subplot(222)
    ax1.scatter(mca_2d[0], mca_2d[1])

    ax1 = fig.add_subplot(223)
    ax1.scatter(mca_2d[0], mca_2d[2])

    ax1 = fig.add_subplot(224)
    ax1.scatter(mca_2d[1], mca_2d[2])

    plt.show()


def extract_plot_test():
    pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8")#.sample(50000)

    print(pd_unique_attributes.describe())
    print(pd_unique_attributes.dtypes)

    accessions = pd_unique_attributes['accession']
    del pd_unique_attributes['accession']

    # model = KernelPCA(n_components=3, kernel='rbf') # memory error
    # model = MDS(n_components=3, n_init=12, max_iter=1200, metric=True, n_jobs=4, random_state=2019) # memory error
    # model = Isomap(n_components=3, n_jobs = 4, n_neighbors = 5) # memory error
    # model = LocallyLinearEmbedding(n_components=3, n_neighbors = 10,method = 'modified', n_jobs = 4,  random_state=2019) # memory error
    # model = LinearDiscriminantAnalysis(n_components=3) # need target labels

    model = PCA(n_components=3)
    # model = NMF(n_components=3, init='random', random_state=0)
    # model = IncrementalPCA(n_components=3)
    # model = SparsePCA(n_components=3, alpha=0.0001, random_state=2019, n_jobs=-1)
    # model = TruncatedSVD(n_components=3,algorithm='randomized', random_state=2019, n_iter=5)
    # model = GaussianRandomProjection(n_components=3,eps = 0.5, random_state=2019)
    # model = SparseRandomProjection(n_components=3,density = 'auto', eps = 0.5, random_state=2019, dense_output = False)
    # model = MiniBatchDictionaryLearning(n_components=3,batch_size = 200,alpha = 1,n_iter = 25,  random_state=2019)
    # model = FastICA(n_components=154, algorithm = 'parallel',whiten = True,max_iter = 100,  random_state=2019)
    # model = TSNE(n_components=3,learning_rate=300,perplexity = 30,early_exaggeration = 12,init = 'random',  random_state=2019) # expensive, didnt give good results
    transformed_data = model.fit_transform(pd_unique_attributes)

    fig = plt.figure()
    fig.add_subplot(221, projection='3d').scatter(transformed_data[:, 0], transformed_data[:, 1],  transformed_data[:, 2])
    fig.add_subplot(222).scatter(transformed_data[:, 0], transformed_data[:, 1])
    fig.add_subplot(223).scatter(transformed_data[:, 0], transformed_data[:, 2])
    fig.add_subplot(224).scatter(transformed_data[:, 1], transformed_data[:, 2])

    plt.show()


def extract_cluster_plot():
    # pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8").sample(500000)
    pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8")

    print(pd_unique_attributes.describe())
    print(pd_unique_attributes.dtypes)

    accessions = pd_unique_attributes['accession']
    del pd_unique_attributes['accession']

    model = PCA(n_components=5)
    transformed_data = model.fit_transform(pd_unique_attributes)

    # cluster_model = SpectralClustering(n_clusters=10)  # memory error
    # cluster_model = AffinityPropagation()  # memory error
    # cluster_model = FeatureAgglomeration(n_clusters=5)   # doesn't return labels, but clusters well

    # cluster_model = DBSCAN(eps=0.3, min_samples=1000, metric='euclidean')
    cluster_model = KMeans(n_clusters=20)
    # cluster_model = Birch(n_clusters=10)
    # cluster_model = MeanShift() # very good 4 clusters, though expensive
    cluster_model.fit(transformed_data)

    labels = cluster_model.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)
    print(labels)
    print("no of clusters: %d" % n_clusters_)
    print("noise points: %d" % n_noise_)

    model = PCA(n_components=3)
    transformed_data = model.fit_transform(pd_unique_attributes)

    # save labeled data
    pd_unique_attributes['accession'] = accessions
    pd_unique_attributes['cluster_labels'] = labels
    pd_unique_attributes.sort_values("cluster_labels", inplace=True)
    pd_unique_attributes.to_csv(file_utils.clustered_samples_file, index=False, encoding=file_utils.encoding)

    # fig = plt.figure()
    # fig.add_subplot(221, projection='3d').scatter(transformed_data[:, 0], transformed_data[:, 1],  transformed_data[:, 2], c=(labels + 2) / 20)
    # # fig.add_subplot(222, projection='3d').scatter(transformed_data[:, 0], transformed_data[:, 1],  transformed_data[:, 3], c=(labels + 2) / 20)
    # # fig.add_subplot(223, projection='3d').scatter(transformed_data[:, 0], transformed_data[:, 1],  transformed_data[:, 4], c=(labels + 2) / 20)
    # # fig.add_subplot(224, projection='3d').scatter(transformed_data[:, 2], transformed_data[:, 3],  transformed_data[:, 4], c=(labels + 2) / 20)
    # fig.add_subplot(222).scatter(transformed_data[:, 0], transformed_data[:, 1], c=(labels + 1) / 20)
    # fig.add_subplot(223).scatter(transformed_data[:, 0], transformed_data[:, 2], c=(labels + 1) / 20)
    # fig.add_subplot(224).scatter(transformed_data[:, 1], transformed_data[:, 2], c=(labels + 1) / 20)
    # plt.show()

    transformed_data_df = pd.DataFrame(data=transformed_data, columns=["feature_1", "feature_2", "feature_3"])
    transformed_data_df["labels"] = labels
    transformed_data_df["test"] = labels
    fig = px.scatter_3d(transformed_data_df, x="feature_1", y="feature_2", z="feature_3",
                        color="labels", hover_data=["test"],
                        width=800, height=800)

    # fig.update_layout(
    #     margin=dict(l=80, r=40, t=40, b=40),
    #     paper_bgcolor="LightSteelBlue",
    # )

    # plot(fig, filename='temp-plot.html')
    fig.show()


def hierarchical_clustering():
    pd_unique_attributes = pd.read_csv(file_utils.all_data_file, encoding="utf-8").sample(2000)

    print(pd_unique_attributes.describe())
    print(pd_unique_attributes.dtypes)

    accessions = pd_unique_attributes['accession']
    del pd_unique_attributes['accession']

    # create dendrogram
    dendrogram = sch.dendrogram(sch.linkage(pd_unique_attributes, method='ward'))
    # create clusters
    hc = AgglomerativeClustering(n_clusters=2, affinity='euclidean', linkage='ward')
    # save clusters for chart
    labels = hc.fit_predict(pd_unique_attributes)

    model = PCA(n_components=3)
    transformed_data = model.fit_transform(pd_unique_attributes)

    fig = plt.figure()
    fig.add_subplot(221, projection='3d').scatter(transformed_data[:, 0], transformed_data[:, 1],
                                                  transformed_data[:, 2], c=(labels + 2) / 20)
    fig.add_subplot(222).scatter(transformed_data[:, 0], transformed_data[:, 1], c=(labels + 1) / 20)
    fig.add_subplot(223).scatter(transformed_data[:, 0], transformed_data[:, 2], c=(labels + 1) / 20)
    fig.add_subplot(224).scatter(transformed_data[:, 1], transformed_data[:, 2], c=(labels + 1) / 20)
    plt.show()


def cluster(data):
    # dimensionality reduction for clustering
    # cluster with different algorithms
    # visualize after dimensionality reduction
    extract_features(data, 10)


def extract_features(data, no_of_features):
    print("Extracting features")


def cluster_data(data, no_of_features):
    print("Extracting features")

if __name__ == "__main__":
    main(*sys.argv[1:])
