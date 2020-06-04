import io
import re
import graph_info_csv_helpers as utils
import networkx as nx
import chardet
import tarfile
import urllib.request
from scipy.io import mmread

snap_data_url = "https://sparse.tamu.edu/SNAP?per_page=All"
node_limit = 30000

index_page_parsed = utils.soupify(snap_data_url)

rows = index_page_parsed.find_all('table')[1].find_all('tr')
for i in range(1, len(rows)):
    row = rows[i]
    row_data = [attr for attr in row.find_all('td')]
    name = row_data[1].string
    dataset_index_url = row_data[-1].a.get('href')
    parsed_node_number = int(row_data[3].text.replace(',', ''))
    if parsed_node_number > node_limit:
        # TODO: Write to database that there are too many nodes
        print('too many')
    else:
        with urllib.request.urlopen(dataset_index_url) as tarred_mtx:
            tar_dir = tarfile.open(fileobj=tarred_mtx)
        utils.mtx_tar_dir_to_graph(tar_dir)
        print('Read these in')
