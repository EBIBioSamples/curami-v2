import json
import logging
import pathlib

from curami.commons import file_utils

# this module will breakdown the large json file taken from biosamples export pipeline
export_file_path = "/data/temp/export.json"
chunk_size = 100000


def main():
    create_dirs()
    breakdown_to_smaller_chunks()


def create_dirs():
    pathlib.Path(file_utils.raw_sample_directory).mkdir(parents=True, exist_ok=True)


def breakdown_to_smaller_chunks():
    count = 0
    file_count = 0
    with open(export_file_path, "r") as data_file:
        sample_list = []
        for line in data_file:
            if line == "[\n":  # beginning of the array/document
                logging.info("We are at the beginning of the document")
                continue
            elif line == "]\n" or line == "]":  # end of the array/document
                write_to_file(sample_list, file_count)
                logging.info("We are at the end of the document")
                continue

            if line[-2] == ',':
                sample = json.loads(line[:-2])  # line ends with ,/n
            else:
                sample = json.loads(line[:-1])  # last line with samples

            count = count + 1
            sample_list.append(sample)

            if (count % chunk_size) == 0:
                write_to_file(sample_list, file_count)
                sample_list = []
                file_count = file_count + 1


def write_to_file(sample_list, file_count):
    logging.info("Writing chunk to file filename: %d", file_count)
    with open(file_utils.raw_sample_directory + str(file_count) + file_utils.data_extension, "w") as output:
        output.write(json.dumps(sample_list, indent=4))


if __name__ == '__main__':
    main()
