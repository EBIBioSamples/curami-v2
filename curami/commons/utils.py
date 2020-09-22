import json
import os
import sys

from common_utils import file_utils


def show_queue_progress(q_size, total_records, page_size):
    percentage = (1 - q_size * page_size / total_records) * 100
    completed_requests = total_records / page_size - q_size
    sys.stdout.write("\rPercentage = %d%%, total completed requests = %d" % (percentage, completed_requests))
    sys.stdout.flush()


def show_progress(completed_records, total_records):
    percentage = completed_records * 100.0 / total_records
    sys.stdout.write("\rCompleted %d out of %d, Percentage = %0.2f%%" % (completed_records, total_records, percentage))
    sys.stdout.flush()


def save_status(key, status):
    if os.path.exists(file_utils.status_file):
        with open(file_utils.status_file, 'r') as status_file:
            content = json.load(status_file)
    else:
        content = {}

    with open(file_utils.status_file, 'w') as status_file:
        content[key] = status
        json.dump(content, status_file)


def load_status(key):
    with open(file_utils.status_file, 'r') as status_file:
        content = json.load(status_file)

    if key in content:
        return content[key]
    else:
        return None

