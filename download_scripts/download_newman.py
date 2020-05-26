import bs4
import urllib.request
import zipfile
import networkx as nx
from io import BytesIO

base_url = "http://www-personal.umich.edu/~mejn/netdata/"
with urllib.request.urlopen(base_url) as fp:
    soup = bs4.BeautifulSoup(fp.read().decode('utf-8'))
for link in soup.ul.find_all('a'):
    if link.get('href')[-3:] == 'zip':
        with urllib.request.urlopen(base_url + link.get('href')) as graph_zipped_fp:
            zip_fp = BytesIO(graph_zipped_fp.read())
            graph_zipped = zipfile.ZipFile(zip_fp)
            for file in graph_zipped.infolist():
                if 'gml' in file.filename:
                    labeled = False
                    gml_lines = graph_zipped.read(file.filename).decode('utf-8')
                    if 'label' in gml_lines:
                        labeled = True
                    gml_lines = gml_lines.split('\n')[1:]
                    G = nx.parse_gml(gml_lines, labeled)
                    nx.write_weighted_edgelist(G, '../edge_lists/' + file.filename.split('.')[0] + '.csv',
                                               delimiter=',')

