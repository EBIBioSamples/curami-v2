import json
from curami.commons import file_utils

export_file_path = "/home/isuru/export.20190608T230001Z.json"
chunk_size = 100000


def main(*args):
    breakdown_to_smaller_chunks()


def breakdown_to_smaller_chunks():
    count = 0
    file_count = 0
    with open(export_file_path, "r") as data_file:
        sample_list = []
        for line in data_file:
            if line == "[\n":  # beginning of the array
                continue
            elif line == "]\n" or line == "]": # end of the array
                write_to_file(sample_list, file_count)
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

        # line = data_file.readline()
        #
        # if line == "[\n":
        #     print("Started reading export file")
        # else:
        #     print("Wrong start line: " + line)


def write_to_file(sample_list, file_count):
    with open(file_utils.combined_data_directory + str(file_count) + file_utils.data_extension, "w") as output:
        output.write(json.dumps(sample_list, indent=4))


main()
