import sqlite3
from pathlib import Path
from .config import SQLITE_DB_PATH
from .db import get_connection

CREATE_questions_for_ml = """
CREATE TABLE IF NOT EXISTS questions_for_ml (
    question_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    creation_date TEXT NOT NULL,
    last_activity_date TEXT,
    score INTEGER NOT NULL DEFAULT 0,
    view_count INTEGER NOT NULL DEFAULT 0,
    answer_count INTEGER NOT NULL DEFAULT 0,
    is_answered INTEGER NOT NULL DEFAULT 0,
    has_accepted_answer INTEGER NOT NULL DEFAULT 0,
    hour_of_day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    title_length INTEGER NOT NULL,
    num_tags INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (question_id) REFERENCES questions(question_id)
);
"""

"""
Lê questions + question_tags, aplica limpeza e features e preenche questions_for_ml.
- Duplicados: já evitados por question_id PK na origem.
- Timestamps: já em formato texto ISO na coleta.
- has_accepted_answer: já preenchido na coleta.
- Novas features: hour_of_day, day_of_week, title_length, num_tags.
"""
def run_transform(conn=None):
    own_conn = False

    if conn is None:
        if not SQLITE_DB_PATH.parent.exists():
            SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(SQLITE_DB_PATH))
        conn.row_factory = sqlite3.Row
        own_conn = True

    try:
        conn.execute(CREATE_questions_for_ml)
        conn.execute("DELETE FROM questions_for_ml")

        # Inserir com features derivadas
        conn.execute(
            """
            INSERT INTO questions_for_ml (
                question_id, title, creation_date, last_activity_date,
                score, view_count, answer_count, is_answered, has_accepted_answer,
                hour_of_day, day_of_week, title_length, num_tags
            )
            SELECT
                q.question_id,
                COALESCE(NULLIF(TRIM(q.title), ''), '') AS title,
                q.creation_date,
                q.last_activity_date,
                COALESCE(q.score, 0),
                COALESCE(q.view_count, 0),
                COALESCE(q.answer_count, 0),
                COALESCE(q.is_answered, 0),
                COALESCE(q.has_accepted_answer, 0),
                CAST(strftime('%H', q.creation_date) AS INTEGER) AS hour_of_day,
                CAST(strftime('%w', q.creation_date) AS INTEGER) AS day_of_week,
                LENGTH(COALESCE(q.title, '')) AS title_length,
                COALESCE(tag_counts.cnt, 0) AS num_tags
            FROM questions q
            LEFT JOIN (
                SELECT question_id, COUNT(*) AS cnt
                FROM question_tags
                GROUP BY question_id
            ) tag_counts ON tag_counts.question_id = q.question_id
            WHERE q.creation_date IS NOT NULL AND q.creation_date != ''
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM questions_for_ml").fetchone()[0]
        conn.commit()
        return count

    finally:
        if own_conn:
            conn.close()

def export_csv(output_path=None):
    import csv

    if not SQLITE_DB_PATH.parent.exists():
        SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    path = Path(output_path or SQLITE_DB_PATH.parent / "questions_for_ml.csv")
    path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        conn.execute(CREATE_questions_for_ml)
        rows = conn.execute("SELECT * FROM questions_for_ml").fetchall()

        if not rows:
            return 0

        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows([dict(r) for r in rows])

    return len(rows)


if __name__ == "__main__":
    with get_connection() as conn:
        n = run_transform(conn)
        print(f"Transformação concluída. Registros em questions_for_ml: {n}")
    exported = export_csv()
    print(f"Exportado {exported} linhas para data/questions_for_ml.csv")