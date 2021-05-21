import sqlite3 as db


class PiDB:
    def __init__(self, path):
        self.conn = db.connect(path, isolation_level=None)


    def initDb(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS diskusage(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                used_total INTEGER(2),
                total_total INTEGER(2)
            );
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS diskusage_path(
                diskusage_id INTEGER,
                path_name TEXT(16),
                used INTEGER(2),
                total INTEGER(2),
                FOREIGN KEY(diskusage_id) REFERENCES diskusage(id)
            );
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS netusage(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                r_total INTEGER(2),
                s_total INTEGER(2)
            );
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS netusage_interface(
                diskusage_id INTEGER,
                interface_name TEXT(16),
                r INTEGER(2),
                s INTEGER(2),
                FOREIGN KEY(diskusage_id) REFERENCES diskusage(id)
            );
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS statistics(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                t TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mem_used INTEGER(2) NOT NULL,
                mem_total INTEGER(2) NOT NULL,
                swap_used INTEGER(2) NOT NULL,
                swap_total INTEGER(2) NOT NULL,
                load_one INTEGER(2) NOT NULL,
                load_five INTEGER(2) NOT NULL,
                load_fifteen INTEGER(2) NOT NULL,
                temp INTEGER(2) NOT NULL,
                diskusage_id INTEGER,
                netusage_id INTERGER,
                FOREIGN KEY(diskusage_id) REFERENCES diskusage(id),
                FOREIGN KEY(netusage_id) REFERENCES netusage(id)
            );
        ''')
        self.conn.close()


    def insertIntoDiskUsage(self, **data):
        self.conn.execute("INSERT INTO diskusage(used_total, total_total) VALUES(?, ?)", (data['usage_total'], data['total_total']))
        id_metadata = self.conn.execute("SELECT * FROM diskusage ORDER BY id DESC LIMIT 1").fetchone()[0]
        for path in data['paths']:
            self.conn.execute('''
                INSERT INTO diskusage_path VALUES(?, ?, ?, ?)
            ''', (id_metadata, path['mount_point'], path['used'], path['total']))
        return id_metadata

    
    def insertIntoNetUsage(self, **data):
        self.conn.execute("INSERT INTO netusage(r_total, s_total) VALUES(?, ?)", (data['r_total'], data['s_total']))
        id_metadata = self.conn.execute("SELECT * FROM netusage ORDER BY id DESC LIMIT 1").fetchone()[0]
        for interface in data['interfaces']:
            self.conn.execute('''
                INSERT INTO netusage_interface VALUES(?, ?, ?, ?)
            ''', (id_metadata, interface['name'], interface['received'], interface['sent']))
        return id_metadata


    def insertIntoStatistics(self, **data):
        self.conn.execute('''
            INSERT INTO statistics(
                mem_used, mem_total, 
                swap_used, swap_total, 
                load_one, load_five, load_fifteen,
                temp, 
                diskusage_id, netusage_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['mem_used'], data['mem_total'],
            data['swap_used'], data['swap_total'],
            data['load_one'], data['load_five'], data['load_fifteen'],
            data['temp'],
            data['diskusage_id'], data['netusage_id']
        ))


    def close(self):
        self.conn.close()