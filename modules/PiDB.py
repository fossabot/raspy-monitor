from time import time
from json import dumps
import sqlite3 as db


class PiDB:
    def __init__(self, path):
        self.conn = db.connect(path, isolation_level=None)
        self.query = self.conn.execute
        self.multiQuery = self.conn.executemany
        self.close = self.conn.close


    def initDb(self):
        self.query('''
            CREATE TABLE IF NOT EXISTS statistics(
                t INTEGER PRIMARY KEY NOT NULL,
                mem_used INTEGER(2) NOT NULL,
                mem_total INTEGER(2) NOT NULL,
                swap_used INTEGER(2) NOT NULL,
                swap_total INTEGER(2) NOT NULL,
                load_one INTEGER(2) NOT NULL,
                load_five INTEGER(2) NOT NULL,
                load_fifteen INTEGER(2) NOT NULL,
                temp INTEGER(2) NOT NULL,
                disk JSON NOT NULL,
                disk_used_total INTEGER(2) NOT NULL,
                disk_total_total INTEGER(2) NOT NULL,
                net JSON NOT NULL,
                net_s_total INTEGER(2) NOT NULL,
                net_r_total INTEGER(2) NOT NULL
            );
        ''')


    def insertIntoStatistics(self, **data):
        values = (
            int(time()),
            data['memory']['memory']['used'], data['memory']['memory']['total'],
            data['memory']['swap']['used'], data['memory']['swap']['total'],
            data['cpu']['load']['last_minute'], data['cpu']['load']['last_five_minutes'],
            data['cpu']['load']['last_fifteen_minutes'], data['cpu']['temp'],
            dumps(data['disk']['paths']),
            data['disk']['used_total'], data['disk']['total_total'],
            dumps(data['net']['interfaces']),
            data['net']['sent_total'], data['net']['received_total']
        )
        self.query("INSERT INTO statistics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)


    def getLastDayStatistics(self):
        return self.query("SELECT * FROM statistics WHERE t >= " + str(time() - 86400)).fetchall()
    

    def getLastStatistics(self):
        return self.query("SELECT * FROM statistics ORDER BY t DESC LIMIT 1").fetchone()


    def delOldStatistics(self):
        self.query("DELETE FROM netusage WHERE t < " + str(time() - 86400))
        self.query("DELETE FROM diskusage WHERE t < " + str(time() - 86400))
        self.query("DELETE FROM statistics WHERE t < " + str(time() - 86400))