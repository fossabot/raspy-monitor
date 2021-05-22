from time import time
import sqlite3 as db


class PiDB:
    def __init__(self, path):
        self.conn = db.connect(path, isolation_level=None)
        self.query = self.conn.execute
        self.close = self.conn.close


    def initDb(self):
        self.query('''
            CREATE TABLE IF NOT EXISTS diskusage(
                statistics_id INTEGER,
                path_name TEXT(16),
                used INTEGER(2),
                total INTEGER(2),
                FOREIGN KEY(statistics_id) REFERENCES statistics(id)
            );
        ''')
        self.query('''
            CREATE TABLE IF NOT EXISTS netusage(
                statistics_id INTEGER,
                interface_name TEXT(16),
                r INTEGER(2),
                s INTEGER(2),
                FOREIGN KEY(statistics_id) REFERENCES statistics(id)
            );
        ''')
        self.query('''
            CREATE TABLE IF NOT EXISTS statistics(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                t INTEGER NOT NULL,
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
        self.conn.close()


    def insertIntoDiskUsage(self, **data):
        for path in data['paths']:
            self.query('''
                INSERT INTO diskusage VALUES(?, ?, ?, ?)
            ''', (self.current_statistic_id, path['mount_point'], path['used'], path['total']))

    
    def insertIntoNetUsage(self, **data):        
        for interface in data['interfaces']:
            self.query('''
                INSERT INTO netusage VALUES(?, ?, ?, ?)
            ''', (self.current_statistic_id, interface['name'], interface['received'], interface['sent']))


    def insertIntoStatistics(self, **data):
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
        ''', (
            int(time()),
            data['mem_used'], data['mem_total'],
            data['swap_used'], data['swap_total'],
            data['load_one'], data['load_five'], data['load_fifteen'], data['temp'],
            data['disk_used_total'], data['disk_total_total'],
            data['net_r_total'], data['net_s_total']
        ))
        self.current_statistic_id = self.conn.execute('''
            SELECT id FROM statistics ORDER BY id DESC LIMIT 1
        ''').fetchone()[0]


    def getLastHourStatistics(self):
        return self.query("SELECT * FROM statistics WHERE t >= " + str(time() - 3600)).fetchall()

