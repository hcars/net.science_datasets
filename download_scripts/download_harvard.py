import csv
import urllib.request
import json
import networkx as nx
import graph_info_csv_helpers as utils

__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads datasets from Harvard Dataverse.
"""
base_dir_harvard = '../harvard_networks/'

# This downloads graphML files found by the Harvard Dataverse API
base_url = 'https://dataverse.harvard.edu'
base_dir_graphml_tagged = base_dir_harvard + 'graph_ml_tagged/'
rows = 10
start = 0
page = 1
condition = True  # emulate do-while
while condition:
    url = base_url + '/api/search?q=*&type=file&fq=fileTag:"GraphML"' + "&start=" + str(start)
    data = json.load(urllib.request.urlopen(url))
    total = data['data']['total_count']
    for query_result in data['data']['items']:
        zipped_fp = utils.get_zip_fp(query_result['url'])
        for contents in zipped_fp.infolist():
            if not contents.is_dir():
                name = contents.filename
                url = query_result['url']
                G = nx.parse_graphml(zipped_fp.read(contents.filename).decode('utf-8'))
                edge_path = base_dir_graphml_tagged + 'edge_lists/' + contents.filename.split('.')[-2] + '.csv'
                old_attributes = list(G.nodes)
                G = nx.convert_node_labels_to_integers(G)
                id_mapping = []
                node_list = list(G.nodes)
                for i in range(len(node_list)):
                    id_mapping.append([old_attributes[i], str(node_list[i])])
                node_path = base_dir_graphml_tagged + 'node_id_mappings/' + contents.filename.split('.')[-2] + '.csv'
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
