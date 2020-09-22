import json

import pandas as pd
import matplotlib.pyplot as plt

import file_utils
from curami.commons.mongo_connector import MongoConnector


class CurationStatCollector:
    def __init__(self):
        self.mongo_connector = MongoConnector()

    def get_curation_stats(self):
        processed = 0
        curation_domain_count = {}
        curami_attribute_count = {}
        curami_accession_set = set()
        zooma_accession_set = set()
        for curation in self.mongo_connector.get_curation_records():
            processed += 1
            domain = curation['domain']
            if domain in curation_domain_count:
                curation_domain_count[domain] += 1
            else:
                curation_domain_count[domain] = 1

            if domain == 'self.BiosampleZooma':
                zooma_accession_set.add(curation['sample'])

            if domain == 'self.BiosampleCurami':
                curami_accession_set.add(curation['sample'])
                attribute_pre = curation['curation']['attributesPre'][0]['type']
                attribute_post = curation['curation']['attributesPost'][0]['type']
                key = attribute_pre + ':::' + attribute_post
                if key in curami_attribute_count:
                    curami_attribute_count[key]['count'] += 1
                else:
                    curami_attribute_count[key] = {
                        'attribute_pre': attribute_pre,
                        'attribute_post': attribute_post,
                        'count': 1
                    }

            if processed % 10000 == 0:
                print("Processed count: [%d]\r" % processed, end='')

        curami_pd = pd.DataFrame(curami_attribute_count.values())
        curami_pd.sort_values(by=['count'], inplace=True, ascending=False)
        curami_pd.to_csv("../../data/results/curation_stats_curami_curation_links.csv", index=False)
        with open("../../data/results/curation_stats_domain_count.json", "w") as out:
            out.write(json.dumps({'total_curations': processed,
                                  'curami_affected_samples': len(curami_accession_set),
                                  'zooma_affected_samples': len(zooma_accession_set),
                                  'curation_domains': curation_domain_count}))

    @staticmethod
    def plot_results():
        with open("../../data/results/curation_stats_domain_count.json", "r") as in_json:
            json_result = json.load(in_json)

        json_result = json_result['curation_domains']
        labels = [k + " : " + f'{v:,}' for k,v in json_result.items()]
        sizes = list(json_result.values())
        patches, text = plt.pie(sizes, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        # plt.show()
        plt.savefig(file_utils.results_directory + "curation_stats_domain_count.png")


if __name__ == '__main__':
    collector = CurationStatCollector()
    collector.get_curation_stats()
    collector.plot_results()
