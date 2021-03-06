import csv
import io
import sqlite3 as db
import traceback
import urllib.request
import zipfile
from io import BytesIO

import bs4
import chardet
import networkx as nx
from scipy.io import mmread

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


def insert_into_metadata_db(file_path, graph_name, graph_url):
    conn = db.connect('../graph_metadata.db')
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO associated_data VALUES (?, ?, ?)", (file_path, graph_name, graph_url)
        )
        conn.commit()
    except db.IntegrityError as e:
        print(e)
    finally:
        conn.close()


def insert_into_undownloaded_db(name, url, downloaded, file_size):
    conn = db.connect('../graph_metadata.db')
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
        cursor.execute(
            "UPDATE graphs_downloaded SET directed=?, multigraph=?, num_nodes=?, num_self_loops=? WHERE name=? AND "
            "url=?", (directed, multigraph, num_nodes, num_self_loops, name, url)
        )
        print(e)
        print("Updated entry.")
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
                nx.write_edgelist(G, '..' + dir_name + '/edge_lists/' + url.split('/')[-1] + '.csv',
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
            mtx_str = str(zip_dir.read(file.filename))
            with open('temp.mtx', 'w') as out_fp:
                out_fp.write(mtx_str)
            yield mmread_safer_file('temp.mtx'), file.filename


def mtx_tar_dir_to_graph(tar_dir):
    for member in tar_dir.getmembers():
        if member.name[-3:].lower() == 'mtx':
            file_obj = tar_dir.extractfile(member)
            file_bytes = io.BytesIO(file_obj.read())
            # file_str = file_bytes.decode(chardet.detect(file_bytes)['encoding'])
            yield mmread_safer(file_bytes), member.name


def mmread_safer(file_bytes):
    try:
        return mmread(file_bytes)
    except ValueError as e:
        if e == ValueError('source is not in Matrix Market format'):
            my_bytes = file_bytes.getbuffer()
            fixed_bytes = b"%" + my_bytes
            return mmread(fixed_bytes)


def mmread_safer_file(file):
    try:
        return mmread(file)
    except ValueError as e:
        if str(e) == 'source is not in Matrix Market format':
            with open(file, 'r') as in_fp:
                file_lines = str(in_fp.read())
            with open('temp_file', 'w') as out_fp:
                out_fp.write("%")
                out_fp.write(file_lines)
            return mmread('temp_file')


def node_id_write(G, url, edge_list_path, node_id_path, name):
    # old_attributes = list(G.nodes)
    # G = nx.convert_node_labels_to_integers(G)
    # id_mapping = []
    # node_list = list(G.nodes)
    # for i in range(len(node_list)):
    #     id_mapping.append([old_attributes[i], str(node_list[i])])
    # mapping_file = open(node_id_path + name + '.csv',
    #                     'w',
    #                     newline='')
    # mapping_file_writer = csv.writer(mapping_file)
    # mapping_file_writer.writerow(['id', 'name'])
    # for tup in id_mapping:
    #     mapping_file_writer.writerow(list(tup))
    # mapping_file.close()
    nx.write_edgelist(G, edge_list_path + name + '.csv', delimiter=',')
    insert_into_db(name, url, edge_list_path + name + '.csv',
                   node_id_path + name + '.csv',
                   G.is_directed(),
                   G.is_multigraph(), int(G.number_of_nodes()), int(nx.number_of_selfloops(G)))
    return G
