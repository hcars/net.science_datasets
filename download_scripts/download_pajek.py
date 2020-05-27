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
    if href[-3:].lower() == 'ged':
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
        parsed_new_page = utils.soupify(base_url + link.get('href'))
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
            to_delete = []
            # for node in G.nodes:
            #     tmp = node.replace(" ", "").replace("'", '').replace("-",'')
            #     if not tmp.isalnum():
            #         to_delete.append(node)
            #         continue
            # G.remove_nodes_from(to_delete)
            old_attributes = list(G.nodes)
            G = nx.convert_node_labels_to_integers(G)
            id_mapping = []
            node_list = list(G.nodes)
            for i in range(len(node_list)):
                id_mapping.append([old_attributes[i], str(node_list[i])])
            mapping_file = open('../pozo_networks/node_id_mappings/mapping_' + url.split('/')[-1] + '.csv', 'w',
                                newline='')
            mapping_file_writer = csv.writer(mapping_file)
            mapping_file_writer.writerow(['id', 'name'])
            for tup in id_mapping:
                mapping_file_writer.writerow(list(tup))
            nx.write_weighted_edgelist(G, '../pozo_networks/edge_lists/' + url.split('/')[-1] + '.csv',
                                       delimiter=',')
            utils.write_entry(name, url, '/pozo_networks/edge_lists/' + url.split('/')[-1] + '.csv',
                              '/pozo_networks/node_id_mappings/mapping_' + url.split('/')[-1] + '.csv', G.is_directed(),
                              G.is_multigraph(),  int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
        except Exception as e:
            traceback.print_exc()
            print(e)
            print("Couldn't parse " + url)
