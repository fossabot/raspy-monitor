import sqlite3 as db


class PiDB:
    def __init__(self, path):
        self.conn = db.connect(path, isolation_level=None)


    def initDb(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS diskusage(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usage_total INTEGER(2)
            );
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS diskusage_path(
                diskusage_id INTEGER,
                interface_name TEXT(16),
                usage INTEGER(2),
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


    def query(self, sql):
        self.out = self.conn.execute(sql)


    def out(self):
        return self.out


    def close(self):
        self.conn.close()