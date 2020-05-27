import csv
import pandas as pd
__author__ = "Henry Carscadden"
__email__ = "hlc5v@virginia.edu"
"""
This is a utility file for I/O on the csv containing the graph metadata.
"""



csv_filepath = '../graph_info.csv'


def read_master_csv():
    global csv_filepath
    csv_reader = csv.DictReader(open(csv_filepath, 'r'))
    return csv_reader


def check_in_csv(network_name):
    lines = list(read_master_csv())
    for i in range(len(lines)):
        if network_name == lines[i]['network_name']:
            return i
    else:
        return -1


def write_entry(*args):
    global csv_filepath
    in_csv = check_in_csv(args[0])
    if in_csv == -1:
        csv_writer = csv.writer(open(csv_filepath, 'a', newline=''))
        csv_writer.writerow(args)
    else:
        graph_metadata = pd.read_csv(csv_filepath, delimiter=',', header=0)
        graph_metadata.loc[in_csv] = args
        graph_metadata.to_csv(csv_filepath, index=False)