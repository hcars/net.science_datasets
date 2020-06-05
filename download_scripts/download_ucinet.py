import graph_info_csv_helpers as utils
import urllib.request
import igraph
import os

base_url = "http://vlado.fmf.uni-lj.si/pub/networks/data/ucinet/"

ucinet_parsed = utils.soupify(base_url + "ucidata.htm")

for link in ucinet_parsed.find_all('a'):
    link_href = link.get('href')
    if link_href is not None:
        ext = link_href[-3:].lower()
        if ext == 'dat':
            with urllib.request.urlopen(base_url + link_href.split('/')[-1]) as dat_fp:
                file_data = dat_fp.read().decode('utf-8')
            with open('../dl_files/' + link_href.split('/')[-1] + '.dl', 'w', newline='') as tmp_fp:
                tmp_fp.write(file_data)

