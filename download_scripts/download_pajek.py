import csv
import traceback
import urllib.request
import networkx as nx
import numpy as np
import tarfile
import re
import io
import os.path
import graph_info_csv_helpers as utils

__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads Pajek datasets from RPozo's links.
"""
edge_list_path = '../pajek_networks/edge_lists/'
node_id_path = '../pajek_networks/node_id_mappings/'
snap_data_url = "https://sparse.tamu.edu/Pajek?per_page=All"
bytes_limit = 2000000

index_page_parsed = utils.soupify(snap_data_url)

rows = index_page_parsed.find_all('table')[1].find_all('tr')
for i in range(1, len(rows)):
    row = rows[i]
    row_data = [attr for attr in row.find_all('td')]
    name = row_data[1].string
    multigraph = 'multigraph' in row_data[6].string.lower()
    dataset_url = row.find_all('a')[-1].get('href')
    site = urllib.request.urlopen(dataset_url)
    metadata = site.info()
    if int(metadata['Content-Length']) > bytes_limit:
        file_size = metadata['Content-Length']
        utils.insert_into_undownloaded_db(name, dataset_url, 0, file_size)
    else:
        ext = dataset_url[-3:].lower()
        if ext == ".gz":
            with urllib.request.urlopen(dataset_url) as tarred_mtx:
                tar_dir = tarfile.open(fileobj=io.BytesIO(tarred_mtx.read()))
        for mtx, member_name in utils.mtx_tar_dir_to_graph(tar_dir):
            try:
                if type(mtx) is not np.ndarray:
                    mtx = mtx.toarray()
                if mtx.shape[0] != mtx.shape[1]:
                    if 'name' not in member_name:
                        np.save(edge_list_path + 'meta_' + name, mtx)
                    else:
                        network_path = edge_list_path + name + '.csv'
                        if os.path.isfile(network_path):
                            print(mtx)
                            G = nx.read_weighted_edgelist(network_path, delimiter=',')
                            print(list(G.nodes))
                else:
                    G = nx.from_numpy_array(mtx, parallel_edges=multigraph)
                    G = utils.node_id_write(G, dataset_url, edge_list_path, node_id_path, name)
            except Exception as e:
                print(e)
                print("Couldn't parse into graph.")


def pajek_to_files(name, url, pajek_lines):
    if pajek_lines:
        try:
            check_matrix = pajek_lines.find('*matrix')
            if check_matrix != -1:
                pajek_lines = pajek_lines[check_matrix + 6:].strip(' ').strip('\r').strip('\n')
                matrix_lines = pajek_lines.split('\r')
                numbers_exp = re.compile(r'[0-9]')
                append = ";"
                for i in range(len(matrix_lines)):
                    if numbers_exp.search(matrix_lines[i]):
                        matrix_lines[i] = matrix_lines[i].strip('\n') + append
                    else:
                        matrix_lines[i] = ''
                matrix_lines = list(filter(lambda x: x is not '', matrix_lines))
                adj_matrix = " ".join(matrix_lines)
                adj_matrix = adj_matrix[:len(adj_matrix) - 1]
                # print(np.matrix(adj_matrix))
                G = nx.from_numpy_array(np.matrix(adj_matrix))
            else:
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

#
# pajek_lines = []
# base_url = "http://vlado.fmf.uni-lj.si/pub/networks/data/"
# parsed_html = utils.soupify(base_url)
# for link in parsed_html.table.find_all('a'):
#     href = link.get('href')
#     if href[-3:].lower() == 'ged':
#         continue
#     elif href[-3:].lower() == 'zip':
#         url = base_url + link.get('href')
#         name = link.string
#         pajek_lines = utils.get_zipped_pajek_from_url(url)
#         pajek_to_files(name, url, pajek_lines)
#     elif href[-3:].lower() == 'paj':
#         url = base_url + link.get('href')
#         name = link.string
#         pajek_lines = utils.get_pajek_from_url(url)
#         pajek_to_files(name, url, pajek_lines)
#     elif href[-3:].lower() == 'net':
#         url = base_url + link.get('href')
#         name = link.string
#         pajek_lines = utils.get_pajek_from_url(url)
#         pajek_to_files(name, url, pajek_lines)
#     elif href[-3:].lower() == 'htm':
#         name = link.string
#         new_page = link.get('href')
#         if new_page[0] == '.':
#             new_page = base_url + new_page[1:]
#         parsed_new_page = utils.soupify(new_page)
#         for new_link in parsed_new_page.find_all('a'):
#             if new_link.get('href') is not None and 'default.htm' not in new_link.get('href'):
#                 url = new_link.get('href')
#                 if url[0] == '.':
#                     url = "/".join(filter(lambda x: '.htm' not in x, (new_page + url[1:]).split('/')))
#                 if 'vlado.fmf.uni-lj.si' in url:
#                     ext = url[-3:].lower()
#                     if ext == 'net':
#                         pajek_lines = utils.get_pajek_from_url(url)
#                         pajek_to_files(name, url, pajek_lines)
#                     elif ext == 'zip':
#                         list_of_lines = utils.get_zipped_pajek_from_url(url)
#                         for pajek_lines in list_of_lines:
#                             pajek_to_files(name, url, pajek_lines)
#                     elif ext == 'paj':
#                         pajek_lines = utils.get_pajek_from_url(url)
#                         pajek_to_files(name, url, pajek_lines)
#
# pajek_to_files('The NBER U.S. Patent Citations Data File',
#                'http://vlado.fmf.uni-lj.si/pub/networks/data/patents/Patents.htm',
#                utils.get_zipped_pajek_from_url('http://vlado.fmf.uni-lj.si/pub/networks/data/patents/patentsNET.zip'))
# pajek_to_files('Geom Collaboration network in computational geometry',
#                'http://vlado.fmf.uni-lj.si/pub/networks/data/collab/geom.htm',
#                utils.get_zipped_pajek_from_url('http://vlado.fmf.uni-lj.si/pub/networks/data/collab/Geom.zip'))
# pajek_to_files('EAT The Edinburgh Associative Thesaurus',
#                'http://vlado.fmf.uni-lj.si/pub/networks/data/dic/eat/Eat.htm',
#                utils.get_zipped_pajek_from_url('http://vlado.fmf.uni-lj.si/pub/networks/data/dic/eat/EATnew.zip'))
