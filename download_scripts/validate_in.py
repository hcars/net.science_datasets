from glob import glob
import sqlite3 as db

conn = db.connect('../graph_metadata.db')
cursor = conn.cursor()

for edge_list in glob('../*networks/edge_lists/*'):
         print(cursor.execute('SELECT name FROM graphs_downloaded WHERE edgelist_path=?', (edge_list,)))







