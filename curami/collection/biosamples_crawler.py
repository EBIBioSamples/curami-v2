import json
import time

import requests

from curami.commons import utils, file_utils
from curami.commons.config_params import BIOSAMPLES_URL

"""Crawl biosamples public api to get all samples and save them in filesystem. Uses single thread and cursor to avoid 
server timeout errors in multi-threaded paged method. Therefore could run for a long time. See :module:`crawl.py` 
for multi-threaded crawler"""


def main():
    biosamples_url = BIOSAMPLES_URL + 'samples'
    page_size = 100

    start = time.time()
    crawler = BioSamplesCrawler(biosamples_url, page_size)
    crawler.get_all_samples()
    end = time.time()
    print("Total elapsed time: " + str(end - start))


class BioSamplesCrawler:
    def __init__(self, base_url, page_size, request_timeout=50, thread_count=4):
        self.base_url = base_url
        self.page_size = page_size
        self.error_threshold = 10

        self.samples_per_file = 100000
        self.thread_count = thread_count
        self.request_timeout = request_timeout
        self.process_status_key = "biosamples_crawler"

    def get_all_samples(self):
        """
        Get all public samples from BioSamples database through JSON API and save them in local files.
        Uses Solr cursor to avoid timeouts of large page numbers. Therefore cant use threads.
        """
        error_count = 0
        file_name_index = 0
        page = 0
        sample_list = []
        next_page = self.base_url + "?size=" + str(self.page_size) + "&cursor="
        total_samples = self.get_sample_count()
        print("Downloading " + str(total_samples) + " samples from " + self.base_url)

        # continue from the last
        last_runtime_status = utils.load_status(self.process_status_key)
        if last_runtime_status:
            next_page = last_runtime_status["url"]
            file_name_index = last_runtime_status["file_index"]
            print("Continuing from the last runtime status: " + str(last_runtime_status))

        while next_page:
            try:
                samples, next_page = self.retrieve_records(next_page)
                sample_list = sample_list + samples
                page += 1
                error_count = 0
                if len(sample_list) >= self.samples_per_file:
                    with open(file_utils.raw_sample_directory + str(file_name_index) + ".txt", "w") as output:
                        output.write(json.dumps(sample_list, indent=4))
                    sample_list = []
                    file_name_index += 1
                    utils.save_status(self.process_status_key, {"url": next_page, "file_index": file_name_index})
            except requests.exceptions.ReadTimeout:
                print("Failed to get the page: " + next_page + " within the given timeout. Retrying....")
                error_count += 1
                if error_count > self.error_threshold:
                    break
                time.sleep(60)
            except requests.exceptions.HTTPError as error:
                print(error)
                print("Internal server error, page: " + next_page + " (mostly because of slow server). Retrying....")
                error_count += 1
                if error_count > self.error_threshold:
                    break
                time.sleep(60)
            except Exception as e:
                print("Failed to get the page: " + next_page + " unknown error: " + str(e))
                if error_count > self.error_threshold:
                    break
                time.sleep(300)
                break

            utils.show_progress(page * self.page_size, total_samples)

    def retrieve_records(self, next_page):
        response = requests.get(next_page, headers={'content-type': 'application/json'}, timeout=self.request_timeout)
        if response.status_code == requests.codes.ok:
            json_output = response.json()
            samples = json_output['_embedded']['samples']
            if 'next' in json_output['_links']:
                next_page = json_output['_links']['next']['href']
            else:
                next_page = ''
            return samples, next_page
        else:
            print("Invalid response code from " + self.base_url)
            response.raise_for_status()

    def get_sample_count(self):
        response = requests.get(self.base_url, params={"size": 1}, timeout=self.request_timeout)
        total_samples = 0

        if response.status_code == requests.codes.ok:
            total_samples = response.json()["page"]["totalElements"]
        else:
            print("Invalid response code from " + self.base_url)
            response.raise_for_status()

        return total_samples


if __name__ == '__main__':
    main()
