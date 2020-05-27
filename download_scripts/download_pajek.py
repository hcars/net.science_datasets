import csv
import traceback
import zipfile

import networkx as nx
from io import BytesIO
import urllib.request
import download_scripts.graph_info_csv_helpers as utils


__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads Pajek datasets.
"""
pajek_lines = []
base_url = "http://vlado.fmf.uni-lj.si/pub/networks/data/"
parsed_html = utils.soupify(base_url)
for link in parsed_html.table.find_all('a'):
    href = link.get('href')
    if href[-3:].lower() =='ged':
        continue
    elif href[-3:].lower() == 'zip':
        url = base_url + link.get('href')
        name = link.string
        utils.get_zipped_pajek_from_url(url)
    elif href[-3:].lower() == 'net':
            url = base_url + link.get('href')
            name = link.string
            pajek_lines = utils.get_pajek_from_url(url)
    elif href[-3:].lower() == 'htm':
        name = link.string
        parsed_new_page = utils.soupify(base_url+ link.get('href'))
        for new_link in parsed_new_page.find_all('a'):
            if new_link.get('href') is not None:
                url = link.get('href') + new_link.get('href')
                if url.split('/')[0] == '.':
                    url = base_url + '/' + url.split('/')[1]
                ext = url[-3:].lower()
                if ext == 'net':
                    pajek_lines = utils.get_pajek_from_url(url)
                elif ext == 'zip':
                    pajek_lines = utils.get_zipped_pajek_from_url(url)
    if pajek_lines:
        try:
            G = nx.parse_pajek(pajek_lines)
            id_mapping = []
            id = 1
            to_delete = []
            for node in G.nodes:
                tmp = node.replace(" ", "").replace("'", '').replace("-",'')
                if not tmp.isalnum():
                    to_delete.append(node)
                    continue
                if not node.isnumeric():
                    id_mapping.append([id, node])
                    id += 1
            G.remove_nodes_from(to_delete)
            mapping_dict = dict(zip(list(map(lambda x: x[1], id_mapping)), list(map(lambda x: x[0], id_mapping))))
            nx.relabel.relabel_nodes(G, mapping_dict, copy=False)
            mapping_file = open('../node_id_mappings/mapping_' + url.split('/')[-1] + '.csv', 'w',
                                newline='')
            mapping_file_writer = csv.writer(mapping_file)
            mapping_file_writer.writerow(['id', 'name'])
            for tup in id_mapping:
                mapping_file_writer.writerow(list(tup))
            if 'Erdos' in url:
                print(list(G.nodes))
            nx.write_weighted_edgelist(G, '../edge_lists/' + url.split('/')[-1] + '.csv',
                                       delimiter=',')
        except Exception as e:
            traceback.print_exc()
            print(e)
            print("Couldn't parse " + url)

