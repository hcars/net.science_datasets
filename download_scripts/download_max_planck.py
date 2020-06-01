import gzip
import networkx as nx
import graph_info_csv_helpers as utils
import urllib.request

facebook_links = "http://socialnetworks.mpi-sws.mpg.de/data/facebook-links.txt.gz"
facebook_post = "http://socialnetworks.mpi-sws.mpg.de/data/facebook-wall.txt.gz"

networks = [facebook_post, facebook_links]

for net in networks:
    with urllib.request.urlopen(net) as net_fp:
        ungzipped = gzip.open(net_fp).read().decode('utf-8').strip('\n').split('\n')
    cleaned = list(map(lambda x: x.replace('\\N', ''), ungzipped))
    name = net.split('/')[-1].split('.')[0]
    G = nx.read_weighted_edgelist(cleaned)
    nx.write_weighted_edgelist(G, '../max_planck_networks/edge_lists/' + name +'.csv'  ,delimiter=',')
    utils.write_entry(name, net, '../max_planck_networks/edge_lists/' + name +'.csv',
                                  '',
                                  G.is_directed(),
                                  G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))