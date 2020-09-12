import sys


def show_queue_progress(q_size, total_records, page_size):
    percentage = (1 - q_size * page_size / total_records) * 100
    completed_requests = total_records / page_size - q_size
    sys.stdout.write("\rPercentage = %d%%, total completed requests = %d" % (percentage, completed_requests))
    sys.stdout.flush()


def show_progress(completed_records, total_records):
    percentage = completed_records * 100.0 / total_records
    sys.stdout.write("\rCompleted %d out of %d, Percentage = %d%%" % (completed_records, total_records, percentage))
    sys.stdout.flush()
