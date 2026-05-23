import sqlite3
import json
import os
from pathlib import Path
from threading import Lock


class Memory:
    _instances = {}
    _lock = Lock()

    def __new__(cls, db_path=None):
        with cls._lock:
            if db_path not in cls._instances:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instances[db_path] = instance
            return cls._instances[db_path]

    def __init__(self, db_path=None):
        if self._initialized:
            return
        db_dir = Path(__file__).parent.parent / "database"
        db_dir.mkdir(exist_ok=True)
        self.db_path = str(db_dir / (db_path or "mirror.db"))
        self._init_db()
        self._initialized = True

    def _init_db(self):
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        if schema_path.exists():
            schema = schema_path.read_text()
            conn = self._get_conn()
            conn.executescript(schema)
            conn.close()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def execute(self, query, params=None):
        params = params or ()
        conn = self._get_conn()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor
        finally:
            conn.close()

    def fetch_one(self, query, params=None):
        params = params or ()
        conn = self._get_conn()
        try:
            return conn.execute(query, params).fetchone()
        finally:
            conn.close()

    def fetch_all(self, query, params=None):
        params = params or ()
        conn = self._get_conn()
        try:
            return conn.execute(query, params).fetchall()
        finally:
            conn.close()

    def row_to_dict(self, row):
        if row is None:
            return None
        return dict(row)

    def rows_to_dicts(self, rows):
        return [dict(r) for r in rows]


class LeadStore:
    def __init__(self, memory):
        self.db = memory

    def insert(self, fb_id, name=None, profile_url=None, group_name=None,
               post_content=None, detected_keywords=None, sentiment=None,
               hotness_score=0):
        existing = self.db.fetch_one(
            "SELECT id FROM leads WHERE fb_id = ?", (fb_id,)
        )
        if existing:
            return existing["id"]

        cursor = self.db.execute(
            """INSERT INTO leads (fb_id, name, profile_url, group_name,
               post_content, detected_keywords, sentiment, hotness_score)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (fb_id, name, profile_url, group_name, post_content,
             detected_keywords, sentiment, hotness_score)
        )
        return cursor.lastrowid

    def update(self, lead_id, **kwargs):
        fields = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [lead_id]
        self.db.execute(
            f"UPDATE leads SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values
        )

    def get_by_id(self, lead_id):
        return self.db.row_to_dict(
            self.db.fetch_one("SELECT * FROM leads WHERE id = ?", (lead_id,))
        )

    def get_by_status(self, status):
        return self.db.rows_to_dicts(
            self.db.fetch_all("SELECT * FROM leads WHERE status = ? ORDER BY hotness_score DESC", (status,))
        )

    def get_hot_leads(self, min_score=70):
        return self.db.rows_to_dicts(
            self.db.fetch_all(
                "SELECT * FROM leads WHERE hotness_score >= ? ORDER BY hotness_score DESC",
                (min_score,)
            )
        )


class ConversationStore:
    def __init__(self, memory):
        self.db = memory

    def add_message(self, lead_id, message, direction, channel="comment", template_used=None):
        self.db.execute(
            """INSERT INTO conversations (lead_id, message, direction, channel, template_used)
               VALUES (?, ?, ?, ?, ?)""",
            (lead_id, message, direction, channel, template_used)
        )

    def get_conversation(self, lead_id):
        return self.db.rows_to_dicts(
            self.db.fetch_all(
                "SELECT * FROM conversations WHERE lead_id = ? ORDER BY created_at",
                (lead_id,)
            )
        )


class NurtureStore:
    def __init__(self, memory):
        self.db = memory

    def schedule(self, lead_id, step, action_type, scheduled_for):
        self.db.execute(
            """INSERT INTO nurture_actions (lead_id, step, action_type, scheduled_for)
               VALUES (?, ?, ?, ?)""",
            (lead_id, step, action_type, scheduled_for)
        )

    def get_pending(self):
        return self.db.rows_to_dicts(
            self.db.fetch_all(
                "SELECT * FROM nurture_actions WHERE status = 'pending' AND scheduled_for <= CURRENT_TIMESTAMP"
            )
        )

    def mark_done(self, action_id):
        self.db.execute(
            "UPDATE nurture_actions SET status = 'done', executed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (action_id,)
        )
