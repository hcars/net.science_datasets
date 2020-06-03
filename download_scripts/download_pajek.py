import csv
import traceback
import zipfile
import networkx as nx
from io import BytesIO
import urllib.request
import os
import graph_info_csv_helpers as utils

__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads Pajek datasets from RPozo's links.
"""


def pajek_to_files(name, url, pajek_lines):
    if pajek_lines:
        try:
            G = nx.parse_pajek(pajek_lines)
            if not nx.is_empty(G):
                old_attributes = list(G.nodes)
                G = nx.convert_node_labels_to_integers(G)
                id_mapping = []
                node_list = list(G.nodes)
                for i in range(len(node_list)):
                    id_mapping.append([old_attributes[i], str(node_list[i])])
                mapping_file = open('../pajek_networks/node_id_mappings/mapping_' + url.split('/')[-1] + '.csv', 'w',
                                    newline='')
                mapping_file_writer = csv.writer(mapping_file)
                mapping_file_writer.writerow(['id', 'name'])
                for tup in id_mapping:
                    mapping_file_writer.writerow(list(tup))
                nx.write_weighted_edgelist(G, '../pajek_networks/edge_lists/' + url.split('/')[-1] + '.csv',
                                           delimiter=',')
                utils.insert_into_db(name, url, '/pajek_networks/edge_lists/' + url.split('/')[-1] + '.csv',
                                  '/pajek_networks/node_id_mappings/mapping_' + url.split('/')[-1] + '.csv',
                                  G.is_directed(),
                                  G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
        except Exception as e:
            traceback.print_exc()
            print(e)
            print("Couldn't parse " + url)


pajek_lines = []
base_url = "http://vlado.fmf.uni-lj.si/pub/networks/data/"
parsed_html = utils.soupify(base_url)
for link in parsed_html.table.find_all('a'):
    href = link.get('href')
    if href[-3:].lower() == 'ged':
        continue
    elif href[-3:].lower() == 'zip':
        url = base_url + link.get('href')
        name = link.string
        pajek_lines = utils.get_zipped_pajek_from_url(url)
        pajek_to_files(name, url, pajek_lines)
    elif href[-3:].lower() == 'paj':
        url = base_url + link.get('href')
        name = link.string
        pajek_lines = utils.get_zipped_pajek_from_url(url)
        pajek_to_files(name, url, pajek_lines)
    elif href[-3:].lower() == 'net':
        url = base_url + link.get('href')
        name = link.string
        pajek_lines = utils.get_pajek_from_url(url)
        pajek_to_files(name, url, pajek_lines)
    elif href[-3:].lower() == 'htm':
        name = link.string
        new_page = link.get('href')
        if new_page[0] == '.':
            new_page = base_url + new_page[1:]
        parsed_new_page = utils.soupify(new_page)
        for new_link in parsed_new_page.find_all('a'):
            if new_link.get('href') is not None and 'default.htm' not in new_link.get('href'):
                url = new_link.get('href')
                if url[0] == '.':
                    url = "/".join(filter(lambda x: '.htm' not in x, (new_page + url[1:]).split('/')))
                if 'vlado.fmf.uni-lj.si' in url:
                    ext = url[-3:].lower()
                    if ext == 'net':
                        pajek_lines = utils.get_pajek_from_url(url)
                    elif ext == 'zip':
                        pajek_lines = utils.get_zipped_pajek_from_url(url)
                    elif ext == 'paj':
                        pajek_lines = utils.get_zipped_pajek_from_url(url)
                    pajek_to_files(name, url, pajek_lines)

pajek_to_files('The NBER U.S. Patent Citations Data File',
               'http://vlado.fmf.uni-lj.si/pub/networks/data/patents/Patents.htm',
               utils.get_zipped_pajek_from_url('http://vlado.fmf.uni-lj.si/pub/networks/data/patents/patentsNET.zip'))
pajek_to_files('Geom Collaboration network in computational geometry',
               'http://vlado.fmf.uni-lj.si/pub/networks/data/collab/geom.htm',
               utils.get_zipped_pajek_from_url('http://vlado.fmf.uni-lj.si/pub/networks/data/collab/Geom.zip'))
pajek_to_files('EAT The Edinburgh Associative Thesaurus',
               'http://vlado.fmf.uni-lj.si/pub/networks/data/dic/eat/Eat.htm',
               utils.get_zipped_pajek_from_url('http://vlado.fmf.uni-lj.si/pub/networks/data/dic/eat/EATnew.zip'))
