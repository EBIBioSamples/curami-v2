import json
import os
import queue
import threading
import time

import requests

from curami.commons import utils, file_utils

"""Crawl biosamples public api to get all samples and save them in filesystem. Uses single thread and cursor to avoid 
server timeout errors in multi-threaded paged method. Therefore could run for a long time. See :class:`crawl.py` 
for multi-threaded crawler"""


def main():
    biosamples_url = 'http://www.ebi.ac.uk/biosamples/samples'
    page_size = 100

    start = time.time()
    crawler = BioSamplesCrawler(biosamples_url, page_size)
    crawler.get_all_samples()
    # crawler.get_all_samples_parallel()
    end = time.time()
    print("Total elapsed time: " + str(end - start))


class BioSamplesCrawler:
    def __init__(self, base_url, page_size, request_timeout=50, thread_count=4):
        self.base_url = base_url
        self.page_size = page_size
        self.error_threshold = 4

        self.samples_per_file = 100000
        self.thread_count = thread_count
        self.request_timeout = request_timeout
        self.total_records = 0  # todo remove
        self.continue_from_page = 8733
        self.parameter_queue = queue.Queue()

    def get_all_samples(self):
        """
        Get all public samples from BioSamples database through JSON API and save them in local files.
        Uses Solr cursor to avoid timeouts of large page numbers. Therefore cant use threads.
        """
        error_count = 0
        file_name_index = 0
        sample_list = []
        next_page = self.base_url + "?size=" + str(self.page_size) + "&cursor="
        total_samples = self.get_sample_count()
        print("Downloading " + str(total_samples) + " samples from " + self.base_url)

        while next_page:
            try:
                samples, next_page = self.retrieve_records(next_page)
                sample_list = sample_list + samples
                error_count = 0
                if len(sample_list) >= self.samples_per_file:
                    with open(file_utils.data_directory + str(file_name_index) + ".json", "w") as output:
                        output.write(json.dumps(sample_list, indent=4))
                    sample_list = []
                    file_name_index += 1
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
                print("Unknown error: " + str(e))
                break

            utils.show_progress(file_name_index * self.samples_per_file, total_samples)

    def get_all_samples_parallel(self):
        """
        Get all public samples from BioSamples database through JSON API and save them in local files.
        This method employs multiple threads and utilises page query parameter in URL.
        BioSamples could timeout when using high page numbers.
        Therefore to collect all samples use get_all_samples() method.
        """
        global total_records

        file_utils.create_data_directory()
        total_records = self.get_sample_count()
        no_of_pages = total_records // self.page_size + 1
        print("Collecting " + str(total_records) + " samples using " + str(no_of_pages) + " http requests")
        for i in range(self.continue_from_page, no_of_pages):  # page counting here
            self.parameter_queue.put({"size": self.page_size, "page": i})  # , "url": base_urls[i % len(base_urls)]

        for i in range(self.thread_count):
            thread = threading.Thread(target=self.worker_thread)
            thread.daemon = True
            thread.start()

        self.parameter_queue.join()
        self.combine_files(100)

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

    def retrieve_and_save_records(self, params):
        response = requests.get(self.base_url, params, timeout=self.request_timeout)

        if response.status_code == requests.codes.ok:
            # print(response.url)
            with open(file_utils.data_directory + str(params["page"]) + ".txt", "w") as output:
                json_output = response.json()
                output.write(json.dumps(json_output["_embedded"]["samples"], indent=4))
        else:
            print("Invalid response code from " + self.base_url)
            response.raise_for_status()

    def worker_thread(self):
        while True:
            params = self.parameter_queue.get()
            try:
                self.retrieve_and_save_records(params)
            except requests.exceptions.ReadTimeout:
                print("Failed to get the page: " + str(params["page"]) + " within the given timeout. Retrying....")
                self.parameter_queue.put(params)
            except requests.exceptions.HTTPError as error:
                print("Internal server error, page: " +
                      str(params["page"]) + " (mostly because of slow server). Retrying....")
                self.parameter_queue.put(params)
            else:
                self.parameter_queue.task_done()

            utils.show_queue_progress(self.parameter_queue.qsize(), total_records, self.page_size)

    @staticmethod
    def combine_files(count):
        file_list = os.listdir(file_utils.data_directory)
        print("Found " + str(len(file_list)) + " files. Aggregating them into " + str(len(file_list) / count) + " files")
        file_count = 0
        sample_list = []
        for i, file_name in enumerate(
                sorted(file_list)):  # for consistency we will sort, but not exactly expected order,
            with open(file_utils.data_directory + file_name, "r") as data_file:
                sample_sub_list = json.load(data_file)
            if ((i + 1) % count) == 0:
                sample_list = sample_list + sample_sub_list
                with open(file_utils.combined_data_directory + str(file_count) + file_utils.data_extension, "w") as output:
                    output.write(json.dumps(sample_list, indent=4))
                sample_list = []
                file_count = file_count + 1
            else:
                sample_list = sample_list + sample_sub_list

            if not sample_list:
                with open(file_utils.combined_data_directory + str(file_count) + file_utils.data_extension,
                          "w") as output:
                    output.write(json.dumps(sample_list, indent=4))


if __name__ == '__main__':
    main()
