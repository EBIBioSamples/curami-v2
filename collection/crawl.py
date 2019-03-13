import os
import sys
import json
import queue
import threading
import requests
import commons.utils as utils
import commons.file_utils as file_utils

base_url = "http://wwwdev.ebi.ac.uk/biosamples/samples"
thread_count = 4
page_size = 100
request_timeout = 50
parameter_queue = queue.Queue()
total_records = 0
error_count = 0  # todo
max_error_count = 4  # todo


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
        with open(file_utils.data_directory + str(params["page"]) + ".txt", "w") as output:
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
            print("Failed to get the page within the given timeout. Retrying....")
            parameter_queue.put(params)
        except requests.exceptions.HTTPError as error:
            print("Internal server error (mostly because of slow server). Retrying....")
            parameter_queue.put(params)
        else:
            parameter_queue.task_done()

        # utils.show_progress((1 - parameter_queue.qsize() * page_size / total_records) * 100)
        utils.show_progress(parameter_queue.qsize(), total_records, page_size)


def get_all_samples():
    """
    Get all public samples from BioSamples database through JSON API and save them in local files.
    """
    global total_records

    file_utils.create_data_directory()
    total_records = get_samples_count()
    no_of_pages = total_records // page_size + 1
    print("Collecting " + str(total_records) + " samples using " + str(no_of_pages) + " http requests")
    for i in range(25374, no_of_pages):
        parameter_queue.put({"size": page_size, "page": i})

    for i in range(thread_count):
        thread = threading.Thread(target=worker_thread)
        thread.daemon = True
        thread.start()

    parameter_queue.join()


def main(*args):
    get_all_samples()


if __name__ == '__main__':
    main(*sys.argv[1:])


# get_all_samples()
# Percentage = 76%, total completed requests = 19376
