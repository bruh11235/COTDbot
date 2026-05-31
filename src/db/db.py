import sys
import atexit
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "db.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
conn: sqlite3.Connection | None = None
cursor: sqlite3.Cursor | None = None


def _connect():
    global conn, cursor
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    atexit.register(conn.close)
    atexit.register(conn.commit)


def get_account_info(discord: str) -> tuple | None:
    try:
        cursor.execute(" SELECT * FROM cfmap WHERE discord = ?",
                       (discord,),
                       )
        return cursor.fetchone()
    except Exception as e:
        print(f"SQLite query failed: {e}", file=sys.stderr)
        return None


def update_mapping(discord: str, codeforces: str):
    try:
        cursor.execute(
            """
                INSERT INTO cfmap(discord, codeforces)
                VALUES (?, ?)
                ON CONFLICT(discord) DO UPDATE 
                SET codeforces = excluded.codeforces
                """,
            (discord, codeforces),
            )
        conn.commit()
    except Exception as e:
        print(f"SQLite query failed: {e}", file=sys.stderr)


def reset_db_field(field: str):
    try:
        cursor.execute(f"UPDATE cfmap SET {field} = 0")
        conn.commit()
    except Exception as e:
        print(f"SQLite query failed: {e}", file=sys.stderr)


def set_problem(contest_id: str, idx: str):
    try:
        cursor.execute(
            """
            INSERT INTO problem(pk, contestID, idx)
            VALUES (?, ?, ?)
            ON CONFLICT(pk) DO UPDATE
            SET codeforces = excluded.codeforces,
                idx = excluded.idx
            """,
            (1, contest_id, idx),
        )
        conn.commit()
    except Exception as e:
        print(f"SQLite query failed: {e}", file=sys.stderr)


def get_problem() -> tuple | None:
    try:
        cursor.execute("SELECT * FROM problem WHERE pk = 1")
        return cursor.fetchone()[1:]
    except Exception as e:
        print(f"SQLite query failed: {e}", file=sys.stderr)
        return None


def init_database():
    if DB_PATH.exists():
        open(DB_PATH, "w").close()
        _connect()

    with open(SCHEMA_PATH, "r") as f:
        cursor.executescript(f.read())
        conn.commit()


_connect()


if __name__ == "__main__":
    init_database()
    cursor.execute('INSERT INTO problem VALUES (1, "N/A", "N/A")')
    conn.commit()
