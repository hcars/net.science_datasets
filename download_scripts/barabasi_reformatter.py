import networkx as nx
from glob import glob
import graph_info_csv_helpers as utils

barabasi_path = '../barabasi_networks/edge_lists/'

for edge_file in glob(barabasi_path):
    G = nx.read_graphml(edge_file)
    nx.write_weighted_edgelist(G, '../barabasi_networks/edge_lists/' + edge_file.split('/')[-1].split('.')[0] + '.csv',
                               delimiter=',')
    utils.insert_into_db(edge_file.split('/')[-1].split('.')[0] + '.csv',
                         "http://networksciencebook.com/translations/en/resources/data.html",
                         '../barabasi_networks/edge_lists/' + edge_file.split('/')[-1].split('.')[0] + '.csv',
                         '', G.is_directed(),
                         G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
