import sqlite3
import json
from datetime import datetime

class MemoryStore:
    def __init__(self, db_path='memory_store.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            format TEXT,
            intent TEXT,
            metadata TEXT,
            extracted_fields TEXT,
            actions TEXT,
            trace TEXT
        )''')
        self.conn.commit()

    def log_entry(self, source, format, intent, metadata, extracted_fields, actions, trace):
        c = self.conn.cursor()
        c.execute('''INSERT INTO logs (timestamp, source, format, intent, metadata, extracted_fields, actions, trace)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (datetime.utcnow().isoformat(), source, format, intent,
                   json.dumps(metadata), json.dumps(extracted_fields), json.dumps(actions), json.dumps(trace)))
        self.conn.commit()

    def get_logs(self, limit=100):
        c = self.conn.cursor()
        c.execute('SELECT * FROM logs ORDER BY id DESC LIMIT ?', (limit,))
        return c.fetchall()

    def close(self):
        self.conn.close() 