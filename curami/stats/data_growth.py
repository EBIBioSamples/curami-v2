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

bsd_samples_all = [{'YEAR': 2014, 'COUNT': 3800000},
                   {'YEAR': 2015, 'COUNT': 4300000},
                   {'YEAR': 2016, 'COUNT': 5200000},
                   {'YEAR': 2017, 'COUNT': 9893276},
                   {'YEAR': 2018, 'COUNT': 11478328},
                   {'YEAR': 2019, 'COUNT': 16000000},
                   {'YEAR': 2020, 'COUNT': 19776973},
                   {'YEAR': 2021, 'COUNT': 0}]

bsd_samples_pub = [{'YEAR': 2014, 'COUNT': 0},
                   {'YEAR': 2015, 'COUNT': 0},
                   {'YEAR': 2016, 'COUNT': 0},
                   {'YEAR': 2017, 'COUNT': 5133958},
                   {'YEAR': 2018, 'COUNT': 6563838},
                   {'YEAR': 2019, 'COUNT': 10677575},
                   {'YEAR': 2020, 'COUNT': 13364057},
                   {'YEAR': 2021, 'COUNT': 0}]


def plot_data_growth(data, file_name):
    data_as_list = {'YEAR': [x['YEAR'] for x in data],
                    'COUNT': [x['COUNT'] / 1000000 for x in data]}

    fig, ax = plt.subplots(figsize=(15, 10))

    b = sns.barplot(data_as_list['YEAR'], data_as_list['COUNT'], palette="Blues_d", ax=ax)
    b.axes.set_title("BioSamples data growth", fontsize=25)
    b.set_xlabel("Year", fontsize=15)
    b.set_ylabel("Samples (millions)", fontsize=15)
    b.tick_params(labelsize=10)
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right", fontsize=7)

    # b = sns.barplot(data_as_list['YEAR'][:7], data_as_list['COUNT'][:7], palette="Blues_d", ax=ax)
    # b.axes.set_title("BioSamples data growth", fontsize=25)
    # b.set_xlabel("Year", fontsize=15)
    # b.set_ylabel("Samples (millions)", fontsize=15)
    # b.tick_params(labelsize=10)
    # b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right", fontsize=7)

    # l = sns.lineplot(x="YEAR", y="COUNT", data=data_as_list)

    plt.tight_layout()
    plt.savefig(file_utils.results_directory + file_name)
    plt.show()





def main(*args):
    plot_data_growth(bsd_samples_all, "data_growth_future.png")
    # plot_data_growth(bsd_samples_pub, "data_growth_pub.png")


if __name__ == "__main__":
    main(*sys.argv[1:])
