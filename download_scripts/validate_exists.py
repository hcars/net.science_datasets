import sqlite3 as db
from os.path import exists
from glob import glob

conn = db.connect('../graph_metadata.db')
try:
    cursor = conn.cursor()
    for row in cursor.execute('SELECT edgelist_path FROM graphs_downloaded;'):
        if not exists(row[0]):
           cursor.execute("DELETE FROM graphs_downloaded WHERE edgelist_path = ?", row)
           conn.commit()
except Exception as e:
    print(e)


