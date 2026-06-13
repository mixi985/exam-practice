# -*- coding: utf-8 -*-
"""手机版 - SQLite 数据库层"""
import sqlite3
import json
import threading
from pathlib import Path
from datetime import datetime
import config

_local = threading.local()


class Database:
    """数据库管理器（线程安全）"""
    def get_connection(self):
        conn = getattr(_local, 'conn', None)
        if conn is None:
            conn = sqlite3.connect(config.DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            _local.conn = conn
        return conn

    def close(self):
        conn = getattr(_local, 'conn', None)
        if conn:
            conn.close()
            _local.conn = None

    def init_db(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER DEFAULT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_type TEXT DEFAULT 'single',
            content TEXT NOT NULL,
            options TEXT DEFAULT '{}',
            answer TEXT DEFAULT '',
            explanation TEXT DEFAULT '',
            category_id INTEGER DEFAULT 1,
            is_favorite INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS wrong_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            wrong_count INTEGER DEFAULT 1,
            last_wrong_time TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS practice_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_practice INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        # 插入默认分类
        cur.execute("SELECT COUNT(*) AS c FROM categories")
        if cur.fetchone()["c"] == 0:
            cur.execute("INSERT INTO categories (name) VALUES (?)",
                       (config.DEFAULT_CATEGORY,))
        # 插入默认统计
        cur.execute("SELECT COUNT(*) AS c FROM practice_stats")
        if cur.fetchone()["c"] == 0:
            cur.execute("INSERT INTO practice_stats (total_practice, correct_count) VALUES (0, 0)")
        conn.commit()
        return True


class CategoryRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_all(self):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM categories ORDER BY id")
        rows = [dict(r) for r in cur.fetchall()]
        # 附加题目数
        for r in rows:
            cur.execute("SELECT COUNT(*) AS c FROM questions WHERE category_id = ?",
                       (r["id"],))
            r["question_count"] = cur.fetchone()["c"]
        return rows

    def add(self, name):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        return cur.lastrowid

    def delete(self, cat_id):
        conn = self.db.get_connection()
        cur = conn.cursor()
        # 将题目移到默认分类
        cur.execute("SELECT id FROM categories WHERE name = ?", (config.DEFAULT_CATEGORY,))
        row = cur.fetchone()
        default_id = row["id"] if row else 1
        cur.execute("UPDATE questions SET category_id = ? WHERE category_id = ?",
                   (default_id, cat_id))
        cur.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        conn.commit()


class QuestionRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_all(self):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM questions ORDER BY id")
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            if r.get("options"):
                try:
                    r["options"] = json.loads(r["options"])
                except:
                    r["options"] = {}
        return rows

    def get_by_category(self, category_id):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM questions WHERE category_id = ? ORDER BY id",
                   (category_id,))
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            if r.get("options"):
                try:
                    r["options"] = json.loads(r["options"])
                except:
                    r["options"] = {}
        return rows

    def get_favorites(self):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM questions WHERE is_favorite = 1 ORDER BY id")
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            if r.get("options"):
                try:
                    r["options"] = json.loads(r["options"])
                except:
                    r["options"] = {}
        return rows

    def count_all(self):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM questions")
        return cur.fetchone()["c"]

    def add_batch(self, questions_data):
        conn = self.db.get_connection()
        cur = conn.cursor()
        for q in questions_data:
            options = q.get("options") or {}
            if isinstance(options, dict):
                options = json.dumps(options, ensure_ascii=False)
            cur.execute("""
                INSERT INTO questions (question_type, content, options, answer,
                                     explanation, category_id, is_favorite)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (q.get("question_type", "single"),
                  q["content"], options,
                  q.get("answer", ""),
                  q.get("explanation", ""),
                  q.get("category_id", 1)))
        conn.commit()
        return len(questions_data)

    def toggle_favorite(self, qid):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT is_favorite FROM questions WHERE id = ?", (qid,))
        row = cur.fetchone()
        if not row:
            return False
        new_state = 0 if row["is_favorite"] else 1
        cur.execute("UPDATE questions SET is_favorite = ? WHERE id = ?",
                   (new_state, qid))
        conn.commit()
        return bool(new_state)

    def delete(self, qid):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM questions WHERE id = ?", (qid,))
        cur.execute("DELETE FROM wrong_questions WHERE question_id = ?", (qid,))
        conn.commit()


class WrongRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_all(self):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT q.*, w.wrong_count, w.last_wrong_time
            FROM wrong_questions w
            JOIN questions q ON q.id = w.question_id
            ORDER BY w.last_wrong_time DESC
        """)
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            if r.get("options"):
                try:
                    r["options"] = json.loads(r["options"])
                except:
                    r["options"] = {}
        return rows

    def record(self, qid):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM wrong_questions WHERE question_id = ?",
                   (qid,))
        row = cur.fetchone()
        if row:
            cur.execute("""
                UPDATE wrong_questions SET wrong_count = wrong_count + 1,
                last_wrong_time = CURRENT_TIMESTAMP WHERE question_id = ?
            """, (qid,))
        else:
            cur.execute("INSERT INTO wrong_questions (question_id) VALUES (?)",
                       (qid,))
        conn.commit()

    def count(self):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM wrong_questions")
        return cur.fetchone()["c"]


class StatsRepository:
    def __init__(self, db: Database):
        self.db = db

    def record(self, is_correct: bool):
        conn = self.db.get_connection()
        cur = conn.cursor()
        col = "correct_count" if is_correct else "total_practice"
        cur.execute(f"UPDATE practice_stats SET {col} = {col} + 1 WHERE id = 1")
        conn.commit()

    def get(self):
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM practice_stats WHERE id = 1")
        row = cur.fetchone()
        if not row:
            return {"total_practice": 0, "correct_count": 0}
        total = row["total_practice"]
        correct = row["correct_count"]
        rate = round(correct * 100.0 / total, 1) if total > 0 else 0
        return {"total_practice": total,
                "correct_count": correct,
                "correct_rate": rate}
