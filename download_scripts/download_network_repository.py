import io
import networkx as nx
import graph_info_csv_helpers as utils


__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads files from a large repository known as network repository.
"""
base_site ="http://networkrepository.com/"
base_url = "http://networkrepository.com/networks.php"

parsed_networks_page = utils.soupify(base_url)
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
                        # TODO: Write to file once Rivanna directory is available
                    for other_files in zip_dir.infolist():
                        ext = other_files.filename[-5:].lower()
                        if ext == 'edges':
                            G = nx.read_weighted_edgelist(io.BytesIO(zip_dir.read(other_files.filename)))
                            # TODO: Write to file once Rivanna directory is available
    except ValueError as e:
        print(e)
    except TypeError as e:
        print(url)
        print(e)


print(tot)