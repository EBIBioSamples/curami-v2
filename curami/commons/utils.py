import sys


def show_progress(percentage):
    sys.stdout.write("\r%d%%" % percentage)
    sys.stdout.flush()


def show_progress(q_size, total_records, page_size):
    percentage = (1 - q_size * page_size / total_records) * 100
    completed_requests = total_records / page_size - q_size
    sys.stdout.write("\rPercentage = %d%%, total completed requests = %d" % (percentage, completed_requests))
    sys.stdout.flush()
