import json
import sys

import pandas as pd
import matplotlib.pyplot as plt

from commons import file_utils

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


def draw_summary():
    print("Generating summary graphs...")
    # draw AV pair count per document vs document count
    # draw most frequent attributes and its counts
    # draw most frequent values and its counts
    # draw most frequent attribute value pairs and its counts

    pd_unique_attributes = pd.read_csv(file_utils.unique_attributes_file, encoding="utf-8")
    pd_unique_attributes.set_index("ATTRIBUTE", drop=True, inplace=True)
    pd_unique_attributes.head(50).plot.bar()
    pd_unique_values = pd.read_csv(file_utils.unique_values_file, encoding="utf-8")
    pd_unique_values.head(50).plot()
    plt.show()


def main(*args):
    print_summary_statistics()
    draw_summary()


if __name__ == "__main__":
    main(*sys.argv[1:])
