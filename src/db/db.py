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


def get_cf_handle(discord: str) -> str | None:
    try:
        cursor.execute(
            "SELECT codeforces FROM cfmap WHERE discord = ?",
            (discord,),
        )
        row = cursor.fetchone()

        if row is None:
            return None
        else:
            return row[0]

    except Exception as e:
        print(f"SQLite query failed: {e}")
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
        print(f"SQLite query failed: {e}")


def delete_mapping(discord: str):
    try:
        cursor.execute(
            """
            DELETE FROM cfmap WHERE discord = ?
            """,
            (discord,),
        )
        conn.commit()

    except Exception as e:
        print(f"SQLite query failed: {e}")


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
