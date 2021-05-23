from time import time
import sqlite3 as db


class PiDB:
    def __init__(self, path):
        self.conn = db.connect(path, isolation_level=None)
        self.query = self.conn.execute
        self.multiQuery = self.conn.executemany
        self.close = self.conn.close


    def initDb(self):
        self.query('''
            CREATE TABLE IF NOT EXISTS diskusage(
                statistics_t INTEGER,
                path_name TEXT(16),
                used INTEGER(2),
                total INTEGER(2),
                FOREIGN KEY(statistics_t) REFERENCES statistics(t)
            );
        ''')
        self.query('''
            CREATE TABLE IF NOT EXISTS netusage(
                statistics_t INTEGER,
                interface_name TEXT(16),
                r INTEGER(2),
                s INTEGER(2),
                FOREIGN KEY(statistics_t) REFERENCES statistics(t)
            );
        ''')
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
                disk_used_total INTEGER(2),
                disk_total_total INTEGER(2),
                net_r_total INTEGER(2),
                net_s_total INTEGER(2)
            );
        ''')
        self.close()


    def insertIntoDiskUsage(self, **data):
        values = []
        for path in data['paths']:
            values.append((self.t, path['mount_point'], path['used'], path['total']))
        
        self.multiQuery("INSERT INTO diskusage VALUES(?, ?, ?, ?)", values)

    
    def insertIntoNetUsage(self, **data):        
        values = []
        for interface in data['interfaces']:
            values.append((self.t, interface['name'], interface['received'], interface['sent']))
        
        self.multiQuery("INSERT INTO netusage VALUES(?, ?, ?, ?)", values)


    def insertIntoStatistics(self, **data):
        self.t = int(time())
        values = (
            self.t,
            data['mem_used'], data['mem_total'],
            data['swap_used'], data['swap_total'],
            data['load_one'], data['load_five'], data['load_fifteen'], data['temp'],
            data['disk_used_total'], data['disk_total_total'],
            data['net_r_total'], data['net_s_total']
        )
        print(values)
        self.query('''
            INSERT INTO statistics(
                t,
                mem_used, mem_total,
                swap_used, swap_total,
                load_one, load_five, load_fifteen, temp,
                disk_used_total, disk_total_total,
                net_r_total, net_s_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', values)


    def getLastHourStatistics(self):
        return self.query("SELECT * FROM statistics WHERE t >= " + str(time() - 3600)).fetchall()

