import os
import io
import numpy as np
import graph_info_csv_helpers as utils
import networkx as nx
import tarfile
import urllib.request

base_dir = '../vanheukelum_networks/'
edge_list_path = base_dir + 'edge_lists/'
node_id_path = base_dir + 'node_id_mappings/'
van_heukelum_url = "https://sparse.tamu.edu/vanHeukelum"
bytes_limit = 2000000

index_page_parsed = utils.soupify(van_heukelum_url)

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
                    network_path = edge_list_path + name + '.csv'
                    if os.path.isfile(network_path):
                        np.save(base_dir + 'metadata_arrays/' + member_name.replace('/', '_'), mtx)
                        utils.insert_into_metadata_db(base_dir + 'metadata_arrays/' + member_name, network_path,
                                                      dataset_url)
                else:
                    G = nx.from_numpy_array(mtx, parallel_edges=multigraph)
                    G = utils.node_id_write(G, dataset_url, edge_list_path, node_id_path, name)
            except Exception as e:
                print(e)
                print("Couldn't parse into graph.")
