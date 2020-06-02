import csv
import io
import urllib.request
import networkx as nx

import graph_info_csv_helpers as utils

__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads datasets from the Uri-Alon website.
"""

networks = {'E. Coli Transcription': [
    'http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/1aorinter_st.txt',
    'http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/colinodesdictionary.txt'],
    'Social Social networks of positive sentiment': [
        'http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/prisoninter_st.txt',
        'http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/leader2inter_st.txt']
    ,
    'Yeast Transcription' : ['http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/yeastinter_st.txt'],
    'Electronic Circuits': [
        'http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/s208_st.txt',
        'http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/s420_st.txt',
        'http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/s838_st.txt'],
    'English Word Adjacency': ['http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/darwinbookinter_st.txt'],
    'French Word Adjacency': ['http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/frenchbookinter_st.txt'],
    'Spanish Word Adjacency': ['http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/spanishbookinter_st.txt'],
    'Japanese Word Adjacency': ['http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/japanesebookinter_st.txt'],
    'Protein Structure': [
        'http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/1a4jinter_st.txt',
        'http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/1eawinter_st.txt',
        'http://www.weizmann.ac.il/mcb/UriAlon/sites/mcb.UriAlon/files/uploads/CollectionsOfComplexNetwroks/1aorinter_st.txt']
}

edge_list_path = networks['E. Coli Transcription'][0]
mapping_path = networks['E. Coli Transcription'][1]

with urllib.request.urlopen(edge_list_path) as e_coli_fp:
    lines = e_coli_fp.read()
G = nx.read_weighted_edgelist(io.BytesIO(lines), delimiter=' ')
nx.write_weighted_edgelist(G, '../uri_alon_networks/edge_lists/e_coli_interaction.txt', delimiter=',')
with urllib.request.urlopen(mapping_path) as mapping_fp:
    mapping_lines = mapping_fp.read().decode('utf-8').split('\n')
with open('../uri_alon_networks/node_id_mappings/mapping_e_coli_interaction.txt', 'w') as e_coli_mapping_fp:
    e_coli_mapping_fp.writelines(map(lambda x: x.replace(' ', ',') + '\n', mapping_lines))
utils.insert_into_db('E. Coli Transcription', edge_list_path, '/uri_alon_networks/edge_lists/e_coli_interaction.txt',
                  '/uri_alon_networks/node_id_mappings/mapping_e_coli_interaction.txt', G.is_directed(),
                  G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
for net in networks.keys():
    if net != 'E. Coli Transcription':
        for subnet in networks[net]:
            with urllib.request.urlopen(subnet) as subnet_fp:
                lines = subnet_fp.read()
            G = nx.read_weighted_edgelist(io.BytesIO(lines), delimiter=' ')
            nx.write_weighted_edgelist(G, '../uri_alon_networks/edge_lists/' + subnet.split('/')[-1], delimiter=',')
            utils.insert_into_db(net + subnet.split('/')[-1].split('.')[-2], subnet,
                              '../uri_alon_networks/edge_lists/' + subnet.split('/')[-1], ' ', G.is_directed(),
                  G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
