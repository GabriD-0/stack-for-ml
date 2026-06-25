import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from .config import SQLITE_DB_PATH

@contextmanager
def get_connection():
    if not SQLITE_DB_PATH.parent.exists():
        SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Cria as tabelas no banco de dados.
def init_db(conn):
    schema_path = Path(__file__).resolve().parent.parent / "schema" / "init.sql"
    with open(schema_path, encoding="utf-8") as f:
        conn.executescript(f.read())

# Formata o timestamp para o formato YYYY-MM-DD HH:MM:SS.
def _parse_ts(ts):
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return ts

"""
Insere ou atualiza perguntas e associa tags.
questions: lista de dicts com:
    question_id, title, creation_date, last_activity_date,
    score, view_count, answer_count, is_answered, accepted_answer_id, tags
"""
def upsert_questions(conn, questions):
    cursor = conn.cursor()

    for q in questions:
        qid = q["question_id"]
        has_accepted = 1 if q.get("accepted_answer_id") else 0
        creation = _parse_ts(q.get("creation_date"))
        last_activity = _parse_ts(q.get("last_activity_date"))
        cursor.execute(
            """
            INSERT INTO questions ( question_id, title, creation_date, last_activity_date, score, view_count, answer_count, is_answered, has_accepted_answer) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(question_id) DO UPDATE SET
                title = excluded.title,
                last_activity_date = excluded.last_activity_date,
                score = excluded.score,
                view_count = excluded.view_count,
                answer_count = excluded.answer_count,
                is_answered = excluded.is_answered,
                has_accepted_answer = excluded.has_accepted_answer
            """,
            (
                qid,
                q.get("title") or "",
                creation or "",
                last_activity,
                q.get("score", 0),
                q.get("view_count", 0),
                q.get("answer_count", 0),
                1 if q.get("is_answered") else 0,
                has_accepted,
            ),
        )
        tags = q.get("tags") or []

        for tag_name in tags:
            tag_name = (tag_name or "").strip().lower()

            if not tag_name:
                continue

            cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
            cursor.execute("SELECT tag_id FROM tags WHERE name = ?",(tag_name,))
            row = cursor.fetchone()

            if row:
                tag_id = row[0]
                cursor.execute("INSERT OR IGNORE INTO question_tags (question_id, tag_id) VALUES (?, ?)", (qid, tag_id))

def get_connection_path():
    return str(SQLITE_DB_PATH)