import csv
import io
import traceback
import zipfile
from io import BytesIO
import sqlite3 as db
import chardet
import networkx as nx
import pandas as pd
import tarfile
import bs4
from scipy.io import mmread
import urllib.request

__author__ = "Henry Carscadden"
__email__ = "hlc5v@virginia.edu"
"""
This is a utility file for I/O on the csv containing the graph metadata.
"""

csv_filepath = '../graph_info.csv'


def get_zip_fp(url):
    graph_zipped_fp = urllib.request.urlopen(url)
    zip_fp = BytesIO(graph_zipped_fp.read())
    graph_zipped = zipfile.ZipFile(zip_fp)
    return graph_zipped


def get_zipped_pajek_from_url(url):
    try:
        list_of_lines = []
        pajek_lines = []
        graph_zipped = get_zip_fp(url)
        for file in graph_zipped.infolist():
            if file.filename[-3:].lower() == "net" or file.filename[-3:].lower() == "paj":
                try:
                    pajek_lines = graph_zipped.read(file.filename).decode('utf-8')
                    list_of_lines.append(pajek_lines)
                except:
                    pajek_lines = graph_zipped.read(file.filename)
                    pajek_lines = pajek_lines.decode(chardet.detect(pajek_lines)['encoding'])
                    list_of_lines.append(pajek_lines)
        graph_zipped.close()
        return pajek_lines
    except Exception as e:
        print(e)
        return []


def get_pajek_from_url(url):
    try:
        with urllib.request.urlopen(url) as graph_fp:
            pajek_lines = graph_fp.read().decode('utf-8')
        return pajek_lines
    except ValueError as e:
        with urllib.request.urlopen(url) as graph_fp:
            pajek_lines = graph_fp.read()
            pajek_lines = pajek_lines.decode(chardet.detect(pajek_lines)['encoding'])
        return pajek_lines
    except Exception as e:
        print(e)
        return []


def soupify(url):
    with urllib.request.urlopen(url) as fp:
        try:
            soup = bs4.BeautifulSoup(fp.read().decode('utf-8'))
        except:
            soup = bs4.BeautifulSoup(fp.read().decode('utf-16'))
    return soup


def insert_into_undownloaded_db(name, url, downloaded, file_size):
    conn = db.connect('../graph_metadaa.db')
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO large_graphs VALUES ( ?, ?, ?, ?)", (name, url, downloaded, file_size)
        )
        conn.commit()
    except db.IntegrityError as e:
        print(e)
        print("Database constraints violated")
    finally:
        conn.close()


def insert_into_db(name, url, edgelist_path, node_attributes_path, directed, multigraph, num_nodes, num_self_loops):
    params = (name, url, edgelist_path, node_attributes_path, int(directed), int(multigraph), num_nodes, num_self_loops)
    connection = db.connect('../graph_metadata.db')
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO graphs_downloaded VALUES (" + ",".join(("?" for i in range(len(params) + 1)))[:-2] + ")",
            params
        )
        connection.commit()
    except db.IntegrityError as e:
        print(e)
        print("Database constraints violated")
    finally:
        connection.close()


def pajek_to_files(name, url, pajek_lines, dir_name):
    if pajek_lines:
        try:
            G = nx.parse_pajek(pajek_lines)
            if not nx.is_empty(G):
                old_attributes = list(G.nodes)
                G = nx.convert_node_labels_to_integers(G)
                id_mapping = []
                node_list = list(G.nodes)
                for i in range(len(node_list)):
                    id_mapping.append([old_attributes[i], str(node_list[i])])
                mapping_file = open('..' + dir_name + '/node_id_mappings/mapping_' + url.split('/')[-1] + '.csv', 'w',
                                    newline='')
                mapping_file_writer = csv.writer(mapping_file)
                mapping_file_writer.writerow(['id', 'name'])
                for tup in id_mapping:
                    mapping_file_writer.writerow(list(tup))
                nx.write_weighted_edgelist(G, '..' + dir_name + '/edge_lists/' + url.split('/')[-1] + '.csv',
                                           delimiter=',')
                insert_into_db(name, url, dir_name + '/edge_lists/' + url.split('/')[-1] + '.csv',
                               dir_name + '/node_id_mappings/mapping_' + url.split('/')[-1] + '.csv',
                               G.is_directed(),
                               G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
        except Exception as e:
            traceback.print_exc()
            print(e)
            print("Couldn't parse " + url)


def mtx_zip_dir_to_graph(zip_dir):
    for file in zip_dir.infolist():
        if file.filename[-3:].lower() == "mtx":
            yield mmread(io.BytesIO(zip_dir.read(file.filename)))


def mtx_tar_dir_to_graph(tar_dir):
    for member in tar_dir.getmembers():
        if member.name[-3:].lower() == 'mtx':
            file_obj = tar_dir.extractfile(member)
            file_bytes = io.BytesIO(file_obj.read())
            # file_str = file_bytes.decode(chardet.detect(file_bytes)['encoding'])
            yield mmread(file_bytes)



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
    insert_into_db(name, url, edge_list_path + name + '.csv',
                   node_id_path + name + '.csv',
                   G.is_directed(),
                   G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
    return G
