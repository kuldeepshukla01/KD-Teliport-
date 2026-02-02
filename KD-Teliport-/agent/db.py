import sqlite3
import json
from pathlib import Path

class Database:
    def __init__(self, db_path=None):
        if not db_path:
            # Default to ~/.local/share/kali-ai-agent/agent.db
            data_dir = Path("~/.local/share/kali-ai-agent").expanduser()
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = data_dir / "agent.db"
        else:
            self.db_path = Path(db_path)
            
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Table: targets (scope)
        c.execute('''CREATE TABLE IF NOT EXISTS targets
                     (ip TEXT PRIMARY KEY, hostname TEXT, notes TEXT, status TEXT)''')
        
        # Table: findings
        c.execute('''CREATE TABLE IF NOT EXISTS findings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, target_ip TEXT, 
                      title TEXT, description TEXT, severity TEXT, 
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

        # Table: tools (metadata for generated tools)
        c.execute('''CREATE TABLE IF NOT EXISTS tools
                     (name TEXT PRIMARY KEY, description TEXT, language TEXT, 
                      path TEXT, tags TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
                      
        conn.commit()
        conn.close()

    def add_target(self, ip, hostname="", notes=""):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("INSERT OR REPLACE INTO targets (ip, hostname, notes, status) VALUES (?, ?, ?, ?)",
                         (ip, hostname, notes, "active"))
            conn.commit()
        finally:
            conn.close()

    def get_targets(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM targets")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def add_tool_metadata(self, name, description, language, path, tags):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("INSERT OR REPLACE INTO tools (name, description, language, path, tags) VALUES (?, ?, ?, ?, ?)",
                         (name, description, language, str(path), json.dumps(tags)))
            conn.commit()
        finally:
            conn.close()
