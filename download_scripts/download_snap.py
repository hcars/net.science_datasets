import io
import graph_info_csv_helpers as utils
import networkx as nx
import chardet
import tarfile
import urllib.request
import numpy as np



edge_list_path = '../snap_networks/edge_lists/'
node_id_path = '../snap_networks/node_id_mappings/'
snap_data_url = "https://sparse.tamu.edu/SNAP?per_page=All"
bytes_limit = 1000000

index_page_parsed = utils.soupify(snap_data_url)

rows = index_page_parsed.find_all('table')[1].find_all('tr')
for i in range(1, len(rows)):
    row = rows[i]
    row_data = [attr for attr in row.find_all('td')]
    name = row_data[1].string
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
        try:
            for mtx in utils.mtx_tar_dir_to_graph(tar_dir):
                if type(mtx) is not np.ndarray:
                    mtx = mtx.toarray()
                G = nx.from_numpy_matrix(mtx)
                G = utils.node_id_write(G, dataset_url, edge_list_path, node_id_path, name)
        except Exception as e:
            print(e)
            print("Something went wrong trying to read in the matrix") 
