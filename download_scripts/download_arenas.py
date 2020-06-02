import io

import bs4
import urllib.request
import zipfile
import networkx as nx
from io import BytesIO
import csv
import graph_info_csv_helpers as utils

__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads networks from Alex Arena's website and reads into the a buffer;
from the buffer, we extract node attributes and build a graph. The attributes and graph are written to 
file.
"""
data_url = "http://deim.urv.cat/~alexandre.arenas/data/"
base_url = "http://deim.urv.cat/~alexandre.arenas/data/welcome.htm"
parsed_html = utils.soupify(base_url)
for link in parsed_html.find_all('a'):
    if 'zip' in link.get('href'):
        url = data_url + link.get('href')
        pajek_lines = []
        graph_zipped = utils.get_zip_fp(url)
        for file in graph_zipped.infolist():
            ext = file.filename[-3:].lower()
            if ext == "net" or ext == "paj":
                pajek_lines = graph_zipped.read(file.filename).decode('utf-8')
                if 'jazz' in file.filename:
                    pajek_lines = "\n".join(
                        list(map(lambda x: " ".join(x.strip(' ').replace('\t', '').split(' ')),
                                 pajek_lines.split('\n')[3:])))
                    G = nx.parse_edgelist(pajek_lines)
                utils.pajek_to_files(link.string, url, pajek_lines, '/arenas_networks')
            elif ext == 'txt':
                G = nx.read_weighted_edgelist(io.BytesIO(graph_zipped.read(file.filename)))
                nx.write_weighted_edgelist(G, '../arenas_networks/edge_lists/' + file.filename.replace('txt', 'csv'))
                utils.insert_into_db(file.filename, url,
                                  '/arenas_networks/edge_lists/' + file.filename.replace('txt', 'csv'),
                                  '',
                                  G.is_directed(),
                                  G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
