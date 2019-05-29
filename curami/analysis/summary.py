import json
import sys

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# import sys
# sys.path.append("/home/isuru/Projects/curami-v2")
# export PYTHONPATH=/home/isuru/Projects/curami-v2

from curami.commons import file_utils

sample_count_string = "total samples"
av_count_string = "total attributes"
unique_attribute_count_string = "unique attribute count"
unique_value_count_string = "unique value count"


def print_summary_statistics():
    with open(file_utils.summary_file, "r") as summary_file:
        summary = json.load(summary_file)

    total_samples = summary[sample_count_string]
    total_av_pairs = summary[av_count_string]
    total_unique_attributes = summary[unique_attribute_count_string]
    total_unique_values = summary[unique_value_count_string]
    average_av_per_sample = total_av_pairs / total_samples
    highest_av_per_sample = 0
    lowest_av_per_sample = 0

    print("Total samples: " + str(total_samples))
    print("Average attribute/value per sample: " + str(average_av_per_sample))
    print("Highest number of attribute/value per sample: " + str(highest_av_per_sample))
    print("Lowest number of attribute/value per sample: " + str(lowest_av_per_sample))
    print("Total unique attributes: " + str(total_unique_attributes))
    print("Total unique values: " + str(total_unique_values))


def plot_attribute_count_bar_all_steps():
    print("Generating summary graphs...")
    sns.set(style="whitegrid")

    pd_unique_attributes = pd.read_csv(file_utils.unique_attributes_file, encoding="utf-8")
    pd_unique_attributes_simple = pd.read_csv(file_utils.unique_attributes_file_simple, encoding="utf-8")
    pd_unique_attributes_underscore = pd.read_csv(file_utils.unique_attributes_file_underscore, encoding="utf-8")
    pd_unique_attributes_clean = pd.read_csv(file_utils.unique_attributes_file_final, encoding="utf-8")

    fig, ax = plt.subplots(4, 1, figsize=(15, 16))

    # plt.figure(figsize=(9, 5))
    b = sns.barplot(pd_unique_attributes["ATTRIBUTE"][0:50], pd_unique_attributes["COUNT"][0:50], ax=ax[0])
    b.axes.set_title("Original: Attribute Count", fontsize=20)
    b.set_xlabel("Attribute", fontsize=10)
    b.set_ylabel("Count", fontsize=10)
    b.tick_params(labelsize=7)
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right", fontsize=7)
    plt.tight_layout()

    # plt.figure(figsize=(9, 5))
    b = sns.barplot(pd_unique_attributes_simple["ATTRIBUTE"][0:50], pd_unique_attributes_simple["COUNT"][0:50], ax=ax[1])
    b.axes.set_title("Simple: Attribute Count", fontsize=20)
    b.set_xlabel("Attribute", fontsize=10)
    b.set_ylabel("Count", fontsize=10)
    b.tick_params(labelsize=7)
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right", fontsize=7)
    plt.tight_layout()

    # plt.figure(figsize=(9, 5))
    b = sns.barplot(pd_unique_attributes_underscore["ATTRIBUTE"][0:50], pd_unique_attributes_underscore["COUNT"][0:50], ax=ax[2])
    b.axes.set_title("Camel case: Attribute Count", fontsize=20)
    b.set_xlabel("Attribute", fontsize=10)
    b.set_ylabel("Count", fontsize=10)
    b.tick_params(labelsize=7)
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right", fontsize=7)
    plt.tight_layout()

    # plt.figure(figsize=(9, 5))
    b = sns.barplot(pd_unique_attributes_clean["ATTRIBUTE"][0:50], pd_unique_attributes_clean["COUNT"][0:50], ax=ax[3])
    b.axes.set_title("Final: Attribute Count", fontsize=20)
    b.set_xlabel("Attribute", fontsize=10)
    b.set_ylabel("Count", fontsize=10)
    b.tick_params(labelsize=7)
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right", fontsize=7)
    plt.tight_layout()

    plt.savefig(file_utils.results_directory + "attribute_count_bar.png")
    plt.show()


def plot_attribute_count_bar_first_final_steps():
    sns.set(style="whitegrid")

    pd_unique_attributes = pd.read_csv(file_utils.unique_attributes_file, encoding="utf-8")
    pd_unique_attributes_clean = pd.read_csv(file_utils.unique_attributes_file_final, encoding="utf-8")

    plt.figure(figsize=(9, 5))
    b = sns.barplot(pd_unique_attributes["ATTRIBUTE"][0:50], pd_unique_attributes["COUNT"][0:50])
    b.axes.set_title("Original: Attribute Count", fontsize=20)
    b.set_xlabel("Attribute", fontsize=10)
    b.set_ylabel("Count", fontsize=10)
    b.tick_params(labelsize=7)
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right", fontsize=7)
    plt.tight_layout()
    plt.savefig(file_utils.results_directory + "attribute_count_bar_original.png")

    plt.figure(figsize=(9, 5))
    b = sns.barplot(pd_unique_attributes_clean["ATTRIBUTE"][0:50], pd_unique_attributes_clean["COUNT"][0:50])
    b.axes.set_title("Final: Attribute Count", fontsize=20)
    b.set_xlabel("Attribute", fontsize=10)
    b.set_ylabel("Count", fontsize=10)
    b.tick_params(labelsize=7)
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right", fontsize=7)
    plt.tight_layout()
    plt.savefig(file_utils.results_directory + "attribute_count_bar_final.png")

    plt.show()


def plot_attribute_count_table():
    pd_unique_attributes = pd.read_csv(file_utils.unique_attributes_file, encoding="utf-8")
    pd_unique_attributes_clean = pd.read_csv(file_utils.unique_attributes_file_final, encoding="utf-8")


    result = pd.concat([pd_unique_attributes, pd_unique_attributes_clean], axis=1, sort=False)
    # print(result[:50])


    fig, ax = plt.subplots(figsize=(10, 11))
    # fig, ax = plt.figure(figsize=(9, 5))
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    # color_array = np.ones((50,4))

    the_table = plt.table(cellText=result.values[0:50],
                          # rowLabels=pd_unique_attributes.index,
                          # rowColours=pd_unique_attributes.columns,
                          # colColours=plt.cm.BuPu(np.linspace(0, 0.5, 4)),
                          colColours=plt.cm.BuPu([0.2, 0.3, 0.2, 0.3]),
                          # cellColours=color_array,
                          # cellColours=plt.cm.BuPu([0.1, 0.2, 0.1, 0.2, 0.1] * 10),
                          colLabels=result.columns,
                          loc="center")
    fig.tight_layout()
    plt.savefig(file_utils.results_directory + "attribute_table.png")
    plt.show()


def main(*args):
    print_summary_statistics()
    plot_attribute_count_bar_all_steps()
    plot_attribute_count_bar_first_final_steps()
    plot_attribute_count_table()


if __name__ == "__main__":
    main(*sys.argv[1:])
