import csv
import zipfile
from io import BytesIO

import pandas as pd
import bs4
import urllib.request

__author__ = "Henry Carscadden"
__email__ = "hlc5v@virginia.edu"
"""
This is a utility file for I/O on the csv containing the graph metadata.
"""

csv_filepath = '../graph_info.csv'


def get_zipped_pajek_from_url(url):
    try:
        with urllib.request.urlopen(url) as graph_zipped_fp:
            zip_fp = BytesIO(graph_zipped_fp.read())
            graph_zipped = zipfile.ZipFile(zip_fp)
            for file in graph_zipped.infolist():
                if file.filename[-3:].lower() == "net":
                    try:
                        pajek_lines = graph_zipped.read(file.filename).decode('utf-8')
                    except:
                        pajek_lines = graph_zipped.read(file.filename).decode('utf-16')
            return pajek_lines
    except Exception as e:
        print(e)
        return []


def get_pajek_from_url(url):
    try:
        with urllib.request.urlopen(url) as graph_fp:
            pajek_lines = graph_fp.read().decode('utf-8')
        return pajek_lines
    except Exception as e:
        print(e)
        return []


def soupify(url):
    with urllib.request.urlopen(url) as fp:
        try:
            soup = bs4.BeautifulSoup(fp.read().decode('utf-8'))
        except:
            soup = bs4.BeautifulSoup(fp.read().decode('utf-16'))
    return soup


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
