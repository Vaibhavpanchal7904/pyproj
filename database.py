import json
import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "docusense.db"

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                word_count INTEGER NOT NULL,
                character_count INTEGER NOT NULL,
                sentence_count INTEGER NOT NULL,
                paragraph_count INTEGER NOT NULL,
                reading_minutes INTEGER NOT NULL,
                keywords_json TEXT NOT NULL
            )
        """)
        conn.commit()

def save_analysis(filename, word_count, character_count, sentence_count,
                  paragraph_count, reading_minutes, keywords):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO analyses
            (filename, word_count, character_count, sentence_count,
             paragraph_count, reading_minutes, keywords_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, word_count, character_count, sentence_count,
            paragraph_count, reading_minutes, json.dumps(keywords, ensure_ascii=False)
        ))
        conn.commit()

def get_history():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, filename, created_at, word_count, character_count,
                   sentence_count, paragraph_count, reading_minutes, keywords_json
            FROM analyses ORDER BY id DESC
        """).fetchall()
    return pd.DataFrame([dict(row) for row in rows])

def delete_history():
    with get_connection() as conn:
        conn.execute("DELETE FROM analyses")
        conn.commit()
