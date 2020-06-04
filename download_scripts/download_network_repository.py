import csv
import io
import networkx as nx
import graph_info_csv_helpers as utils

__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads files from a large repository known as network repository.
"""
base_site = "http://networkrepository.com/"
base_url = "http://networkrepository.com/networks.php"
edge_list_path = '../network_repo_networks/edge_lists/'
node_id_path = '../network_repo_networks/node_id_mappings/'
parsed_networks_page = utils.soupify(base_url)


def node_id_write(G, url, edge_list_path, node_id_path, name):
    old_attributes = list(G.nodes)
    G = nx.convert_node_labels_to_integers(G)
    id_mapping = []
    node_list = list(G.nodes)
    for i in range(len(node_list)):
        id_mapping.append([old_attributes[i], str(node_list[i])])
    mapping_file = open(node_id_path + name + '.csv',
                        'w',
                        newline='')
    mapping_file_writer = csv.writer(mapping_file)
    mapping_file_writer.writerow(['id', 'name'])
    for tup in id_mapping:
        mapping_file_writer.writerow(list(tup))
    mapping_file.close()
    nx.write_weighted_edgelist(G, edge_list_path + name + '.csv')
    utils.insert_into_db(name, url, edge_list_path + name + '.csv',
                      node_id_path + name + '.csv',
                      G.is_directed(),
                      G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
    return G


for header in parsed_networks_page.find_all('h3', class_="heading-xs"):
    link = header.find('a')
    name = link.string
    url = base_site + link.get('href')
    try:
        download_page = utils.soupify(url)
        for link in download_page.find_all('a'):
            links_to = link.get('href')
            if links_to is not None:
                if links_to[-3:].lower() == "zip":
                    zip_dir = utils.get_zip_fp(links_to)
                    for mtx_network in utils.mtx_zip_dir_to_graph(zip_dir):
                        G = nx.from_numpy_matrix(mtx_network.toarray())
                        G = node_id_write(G, links_to, edge_list_path, node_id_path, name)
                    for other_files in zip_dir.infolist():
                        ext = other_files.filename[-5:].lower()
                        if ext == 'edges':
                            G = nx.read_weighted_edgelist(io.BytesIO(zip_dir.read(other_files.filename)))
                            G = node_id_write(G, edge_list_path, node_id_path, name)
                            nx.write_weighted_edgelist(G, edge_list_path + name + '.csv')
                            utils.insert_into_db(name, url, edge_list_path + name + '.csv',
                                              node_id_path + name + '.csv',
                                              G.is_directed(),
                                              G.is_multigraph(), int(G.number_of_nodes()),
                                              int(nx.number_of_selfloops(G)))
    except ValueError as e:
        print(url)
        print(e)
    except TypeError as e:
        print(url)
        print(e)
    except Exception as e:
        print(e)
        print("I'm not sure what went wrong.")
