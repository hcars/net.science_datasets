from glob import glob
import sqlite3 as db

conn = db.connect('../graph_metadata.db')
cursor = conn.cursor()

for edge_list in glob('../*networks/edge_lists/*'):
<<<<<<< HEAD
         print(cursor.execute('SELECT name FROM graphs_downloaded WHERE edgelist_path=?', (edge_list,)))







=======
         cursor.execute('SELECT name FROM graphs_downloaded WHERE edgelist_path=?', (edge_list,))
         print(edge_list)
         print(cursor.fetchone())
>>>>>>> 558066681eaaba102ea5a22817fa67b97915c1dc
