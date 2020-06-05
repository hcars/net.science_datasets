import networkx as nx
from glob import glob
import graph_info_csv_helpers as utils

ucinet_graph_ml_path = '../dl_networks/graph_ml/*'

for graph_ml_file in glob(ucinet_graph_ml_path):
    G = nx.read_graphml(graph_ml_file)
    print(graph_ml_file)
    nx.write_weighted_edgelist(G, '../dl_networks/edge_lists/' + graph_ml_file.split('\\')[-1].split('.')[0] + '.csv',
                               delimiter=',')
    utils.insert_into_db(graph_ml_file.split('\\')[-1].split('.')[0] + '.csv',
                         "http://vlado.fmf.uni-lj.si/pub/networks/data/ucinet/",
                         '../dl_networks/edge_lists/' + graph_ml_file.split('\\')[-1].split('.')[0] + '.csv',
                         '', G.is_directed(),
                         G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
