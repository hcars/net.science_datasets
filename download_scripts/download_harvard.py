import csv
import urllib.request
import json
from os.path import exists
import networkx as nx
import graph_info_csv_helpers as utils

__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads datasets from Harvard Dataverse.
"""
base_dir_harvard = '../harvard_networks/'
max_size = 20000000
# This downloads graphML files found by the Harvard Dataverse API
base_url = 'https://dataverse.harvard.edu'
rows = 10
start = 0
page = 1
condition = True  # emulate do-while
while condition:
    url = base_url + '/api/search?q=*graphml*&type=file' + "&start=" + str(start)
    data = json.load(urllib.request.urlopen(url))
    total = data['data']['total_count']
    for query_result in data['data']['items']:
        if query_result['size_in_bytes'] > max_size:
            continue
        url = query_result['url']
        if query_result['name'][-3:].lower() == 'zip':
            base_dir_graphml_tagged = base_dir_harvard + 'graph_ml_tagged/'
            zipped_fp = utils.get_zip_fp(query_result['url'])
            for contents in zipped_fp.infolist():
                if not contents.is_dir():
                    name = contents.filename
                    base_name = contents.filename.split('.')[-2].replace('/', '-')
                    edge_path = base_dir_graphml_tagged + 'edge_lists/' + base_name + '.csv'

                    if exists(edge_path):
                        continue
                    G = nx.parse_graphml(zipped_fp.read(contents.filename).decode('utf-8'))
        else:
            base_dir_graphml_tagged = base_dir_harvard + 'graph_ml_tagged_non_zipped/'
            base_name = query_result['name'].split('.')[-2].replace('/', '-')
            edge_path = base_dir_graphml_tagged + 'edge_lists/' + base_name + '.csv'
            if exists(edge_path):
                continue
            name = base_name
            with urllib.request.urlopen(url) as graph_ml_fp:
                graph_ml_lines = graph_ml_fp.read().decode('utf-8')
            G = nx.parse_graphml(graph_ml_lines)
        edge_path = base_dir_graphml_tagged + 'edge_lists/' + base_name + '.csv'
        node_path = base_dir_graphml_tagged + 'node_id_mappings/' + base_name + '.csv'
        if exists(edge_path):
            continue
        edge_path = base_dir_graphml_tagged + 'edge_lists/' + base_name + '.csv'
        old_attributes = list(G.nodes)
        G = nx.convert_node_labels_to_integers(G)
        id_mapping = []
        node_list = list(G.nodes)
        for i in range(len(node_list)):
            id_mapping.append([old_attributes[i], str(node_list[i])])
        mapping_file = open(node_path, 'w', newline='')
        mapping_file_writer = csv.writer(mapping_file)
        mapping_file_writer.writerow(['id', 'name'])
        for tup in id_mapping:
            mapping_file_writer.writerow(list(tup))
        mapping_file.close()
        nx.write_weighted_edgelist(G, edge_path, delimiter=',')
        utils.insert_into_db(name, url, edge_path, node_path, G.is_directed(), G.is_multigraph(),
                             int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))

    start += rows
    page += 1
    condition = start < total
