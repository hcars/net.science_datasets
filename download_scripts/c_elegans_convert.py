import csv
from glob import glob
import networkx as nx
import graph_info_csv_helpers as utils

base_dir = '../c_elegans_networks/xls_files/*'
node_id_path = '../c_elegans_networks/node_id_mappings/'
edge_list_path = '../c_elegans_networks/edge_lists/'

for edge_list in glob(base_dir):
    G = nx.read_weighted_edgelist(base_dir)
    print(list(G.edges))
    exit()
    old_attributes = list(G.nodes)
    G = nx.convert_node_labels_to_integers(G)
    id_mapping = []
    node_list = list(G.nodes)
    name = edge_list.split('/')[-1]
    for i in range(len(node_list)):
        id_mapping.append([old_attributes[i], str(node_list[i])])
    mapping_file = open(node_id_path +  name,
                        'w',
                        newline='')
    mapping_file_writer = csv.writer(mapping_file)
    mapping_file_writer.writerow(['id', 'name'])
    for tup in id_mapping:
        mapping_file_writer.writerow(list(tup))
    mapping_file.close()
    nx.write_weighted_edgelist(G, edge_list_path  + name, delimiter=',')
    utils.insert_into_db(name, 'https://www.wormatlas.org/neuronalwiring.html', edge_list_path + name,
                   node_id_path + name + '.csv',
                   G.is_directed(),
                   G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))