import os
import sqlite3
import logging

class FileStorage(object):
    schema = '''
    CREATE TABLE IF NOT EXISTS file(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      file_hash TEXT KEY,
      file_name TEXT,
      file_length INTEGER,
      file_path TEXT,
      created DATE CURRENT_TIMESTAMP);
    '''

    def __init__(self, config):
        self.root = config['root_path']

    def initialize(self):
        dbpath = os.path.join(self.root, 'file.db')
        if not os.path.isdir(self.root):
            os.makedirs(self.root)
        try:
            self.conn = sqlite3.connect(dbpath)
        except:
            logging.error("failed to connect to {0}".format(dbpath))
            return False

        try:
            cur = self.conn.cursor()
            cur.execute(self.schema)
            self.conn.commit()
        except:
            logging.error("failed to init DB".format(dbpath))
            return False

        return True

    def add(self, *args):
        sql = "INSERT INTO file(file_hash,file_name,file_length,file_path) VALUES('{0}','{1}',{2},'{3}')" \
              .format(*args)

        cur = self.conn.cursor()
        try:
            cur.execute(sql)
        except:
            logging.error('sql ({0}) error'.format(sql))
        last_id = cur.lastrowid
        self.conn.commit()

        return last_id

    def get_file_id(self, file_hash):
        sql = "SELECT id FROM file WHERE file_hash='{0}'".format(file_hash)
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
        except:
            logging.error('sql ({0}) error'.format(sql))
            return None

        return cur.fetchone()[0]

    def get(self, file_id):
        sql = "SELECT file_name,file_length,file_path FROM file WHERE id={0}".format(file_id)
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
        except:
            logging.error('sql ({0}) error'.format(sql))
            return None

        row = cur.fetchone()
        return (row[0],row[1],row[2])
