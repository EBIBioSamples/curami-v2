import json
import os
import queue
import sys
import threading

import requests

from curami.commons import utils, file_utils

# Crawl biosamples public api to get all samples and save them in small files.
# Here each request make a new file and save page_size number of samples in that file.
# Then combine_files() will build larger files from these small files for ease of processing and storage.
# Since server times out if we use larger page_size value, we have keep this and thread_count in check

# base_url = "http://wwwdev.ebi.ac.uk/biosamples/samples"
base_url = "http://wp-p2m-40:8081/biosamples/samples"
thread_count = 2
page_size = 100
request_timeout = 50
parameter_queue = queue.Queue()
total_records = 0
error_count = 0  # todo
max_error_count = 4  # todo

continue_from_page = 8733


def main(*args):
    get_all_samples()
    # Combine files after collecting data,
    # This step is not necessary, page size can be set to higher value if server supports it
    # combine_files(100)


def get_samples_count():
    response = requests.get(base_url, params={"size": 1}, timeout=request_timeout)
    total_samples = 0

    if response.status_code == requests.codes.ok:
        total_samples = response.json()["page"]["totalElements"]
    else:
        print("Invalid response code from " + base_url)
        response.raise_for_status()

    return total_samples


def retrieve_and_save_records(params):
    response = requests.get(base_url, params, timeout=request_timeout)

    if response.status_code == requests.codes.ok:
        # print(response.url)
        with open(file_utils.raw_sample_directory_temp + str(params["page"]) + ".txt", "w") as output:
            json_output = response.json()
            output.write(json.dumps(json_output["_embedded"]["samples"], indent=4))
    else:
        print("Invalid response code from " + base_url)
        response.raise_for_status()


def worker_thread():
    while True:
        params = parameter_queue.get()
        try:
            retrieve_and_save_records(params)
        except requests.exceptions.ReadTimeout:
            print("Failed to get the page: " + str(params["page"]) + " within the given timeout. Retrying....")
            parameter_queue.put(params)
        except requests.exceptions.HTTPError as error:
            print("Internal server error, page: " +
                  str(params["page"]) + " (mostly because of slow server). Retrying....")
            parameter_queue.put(params)
        else:
            parameter_queue.task_done()

        utils.show_queue_progress(parameter_queue.qsize(), total_records, page_size)


def get_all_samples():
    """
    Get all public samples from BioSamples database through JSON API and save them in local files.
    """
    global total_records

    file_utils.create_data_directory()
    total_records = get_samples_count()
    no_of_pages = total_records // page_size + 1
    print("Collecting " + str(total_records) + " samples using " + str(no_of_pages) + " http requests")
    for i in range(continue_from_page, no_of_pages):  # page counting here
        parameter_queue.put({"size": page_size, "page": i})  # , "url": base_urls[i % len(base_urls)]

    for i in range(thread_count):
        thread = threading.Thread(target=worker_thread)
        thread.daemon = True
        thread.start()

    parameter_queue.join()


def combine_files(count):
    file_list = os.listdir(file_utils.raw_sample_directory_temp)
    print("Found " + str(len(file_list)) + " files. Aggregating them into " + str(len(file_list) / count) + " files")
    file_count = 0
    sample_list = []
    for i, file_name in enumerate(sorted(file_list)):  # for consistency we will sort, but not exactly expected order,
        with open(file_utils.raw_sample_directory_temp + file_name, "r") as data_file:
            sample_sub_list = json.load(data_file)
        if ((i + 1) % count) == 0:
            sample_list = sample_list + sample_sub_list
            with open(file_utils.raw_sample_directory + str(file_count) + file_utils.data_extension, "w") as output:
                output.write(json.dumps(sample_list, indent=4))
            sample_list = []
            file_count = file_count + 1
        else:
            sample_list = sample_list + sample_sub_list

    if sample_list:
        with open(file_utils.raw_sample_directory + str(file_count) + file_utils.data_extension, "w") as output:
            output.write(json.dumps(sample_list, indent=4))

    print("All smaller files were aggregated into larger files. " +
          "You can now safely delete " + file_utils.raw_sample_directory_temp + " directory")


if __name__ == '__main__':
    main(*sys.argv[1:])
