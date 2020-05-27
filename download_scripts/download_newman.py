import bs4
import urllib.request
import zipfile
import networkx as nx
from io import BytesIO
import csv
import download_scripts.graph_info_csv_helpers as utils

__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads networks from Newman's website and reads into the a buffer;
from the buffer, we extract node attributes and build a graph. The attributes and graph are written to 
file.
"""

base_url = "http://www-personal.umich.edu/~mejn/netdata/"
with urllib.request.urlopen(base_url) as fp:
    soup = bs4.BeautifulSoup(fp.read().decode('utf-8'))
for link in soup.ul.find_all('a'):
    if link.get('href')[-3:] == 'zip':
        with urllib.request.urlopen(base_url + link.get('href')) as graph_zipped_fp:
            url = base_url + link.get('href')
            name = link.string
            zip_fp = BytesIO(graph_zipped_fp.read())
            graph_zipped = zipfile.ZipFile(zip_fp)
            for file in graph_zipped.infolist():
                if 'gml' in file.filename:
                    try:
                        label = 'id'
                        gml_lines = graph_zipped.read(file.filename).decode('utf-8')
                        if label in gml_lines:
                            label = 'label'
                        gml_lines = gml_lines.split('\n')[1:]
                        dict, G = nx.parse_gml(gml_lines, label=label)
                    except nx.exception.NetworkXError:
                        gml_lines.insert(2, 'multigraph 1')
                        dict, G = nx.parse_gml(gml_lines, label='id')
                    mapping_file = open('../node_id_mappings/mapping_' + file.filename.split('.')[0] + '.csv', 'w',
                                        newline='')
                    mapping_file_writer = csv.writer(mapping_file)
                    mapping_file_writer.writerow(dict['node'][0].keys())
                    for node in dict['node']:
                        G.add_node(node['id'])
                        mapping_file_writer.writerow(node.values())
                    for edge in dict['edge']:
                        if 'value' in edge.keys():
                            G.add_weighted_edges_from([(edge['source'], edge['target'], edge['value'])])
                        else:
                            G.add_edge(edge['source'], edge['target'])
                    nx.write_weighted_edgelist(G, '../edge_lists/' + file.filename.split('.')[0] + '.csv',
                                               delimiter=',')
                    mapping_file.close()
                    utils.write_entry(name, url, 'edge_lists/' + file.filename.split('.')[0] + '.csv',
                                      'node_id_mappings/mapping_' + file.filename.split('.')[0] + '.csv',
                                      G.is_directed(), G.is_multigraph(), G.number_of_nodes())
