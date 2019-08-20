import sys
import json

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from tqdm import tqdm
from sklearn.decomposition import PCA

#plotly imports
import plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

import file_utils

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

    del pd_unique_attributes['accession']

    kmeans = KMeans(n_clusters=10, random_state=0).fit(pd_unique_attributes)
    clusters = kmeans.predict(pd_unique_attributes)
    pd_unique_attributes["cluster"] = clusters

    plot_samples = pd_unique_attributes.sample(5000)
    pca_2d = PCA(n_components=2)
    PCs_2d = pd.DataFrame(pca_2d.fit_transform(plot_samples.drop(["cluster"], axis=1)))
    PCs_2d.columns = ["PC1_2d", "PC2_2d"]
    plot_samples = pd.concat([plot_samples, PCs_2d], axis=1, join='inner')

    cluster0 = plot_samples[plot_samples["cluster"] == 0]
    cluster1 = plot_samples[plot_samples["cluster"] == 1]
    cluster2 = plot_samples[plot_samples["cluster"] == 2]

    trace1 = go.Scatter(
        x=cluster0["PC1_2d"],
        y=cluster0["PC2_2d"],
        mode="markers",
        name="Cluster 0",
        marker=dict(color='rgba(255, 128, 255, 0.8)'),
        text=None)

    # trace2 is for 'Cluster 1'
    trace2 = go.Scatter(
        x=cluster1["PC1_2d"],
        y=cluster1["PC2_2d"],
        mode="markers",
        name="Cluster 1",
        marker=dict(color='rgba(255, 128, 2, 0.8)'),
        text=None)

    # trace3 is for 'Cluster 2'
    trace3 = go.Scatter(
        x=cluster2["PC1_2d"],
        y=cluster2["PC2_2d"],
        mode="markers",
        name="Cluster 2",
        marker=dict(color='rgba(0, 255, 200, 0.8)'),
        text=None)

    data = [trace1, trace2, trace3]

    title = "Visualizing Clusters in Two Dimensions Using PCA"

    layout = dict(title=title,
                  xaxis=dict(title='PC1', ticklen=5, zeroline=False),
                  yaxis=dict(title='PC2', ticklen=5, zeroline=False)
                  )

    fig = dict(data=data, layout=layout)

    plot(fig)


    print(kmeans.labels_)
    print(kmeans.cluster_centers_)

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


def generate_all_data_file(from_file_no, to_file_no):
    clean_attribute_map = {}
    attribute_clenup_df = pd.read_csv(file_utils.unique_attributes_file_final_diff_all, encoding=file_utils.encoding)
    for index, row in attribute_clenup_df.iterrows():
        for i, x in enumerate(row):
            if i != 0 and x != '' and x == x:  # nan check x == x
                clean_attribute_map[x] = row[0]

    pd_unique_attributes = pd.read_csv(file_utils.unique_attributes_file_final)
    columns = pd_unique_attributes["ATTRIBUTE"][0:100].tolist()
    columns_set = set(columns)

    data_list = []
    for i in tqdm(range(from_file_no, to_file_no + 1)):
        with open(file_utils.combined_data_directory + str(i) + file_utils.data_extension, "r") as data_file:
            sample_list = json.load(data_file)

        for sample in sample_list:
            attribute_values = sample["characteristics"]

            data_map = {"accession": sample["accession"]}
            for key, value_as_list in attribute_values.items():
                if clean_attribute_map[key] in columns_set:
                    data_map[clean_attribute_map[key]] = int(1)

            data_list.append(data_map)

    pd_data_list = pd.DataFrame(data_list, columns=columns)
    pd_data_list.fillna(int(0), inplace=True)

    with open(file_utils.all_data_file, "w") as output:
        pd_data_list.to_csv(output, index=False, encoding="utf-8", float_format='%.0f')


def main(*args):
    # generate_all_data_file(1, 3)
    cluster()


if __name__ == "__main__":
    main(*sys.argv[1:])
