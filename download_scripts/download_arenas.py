import bs4
import urllib.request
import zipfile
import networkx as nx
import download_scripts.gml
from io import BytesIO
import csv
import download_scripts.graph_info_csv_helpers as utils

__author__ = "Henry Carscadden"
__email__ = 'hlc5v@virginia.edu'
"""
This file downloads networks from Alex Arena's website and reads into the a buffer;
from the buffer, we extract node attributes and build a graph. The attributes and graph are written to 
file.
"""
data_url = "http://deim.urv.cat/~alexandre.arenas/data/"
base_url = "http://deim.urv.cat/~alexandre.arenas/data/welcome.htm"
parsed_html = download_scripts.graph_info_csv_helpers.soupify(base_url)
for link in parsed_html.find_all('a'):
    if 'zip' in link.get('href'):
        url = data_url + link.get('href')
        pajek_lines = []
        graph_zipped = utils.get_zip_fp(url)
        for file in graph_zipped.infolist():
            if file.filename[-3:].lower() == "net" or file.filename[-3:].lower() == "paj":
                    pajek_lines = graph_zipped.read(file.filename).decode('utf-8')
        utils.pajek_to_files(link.string, url, pajek_lines, '/arenas_networks')