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
    cursor.execute(" SELECT * FROM cfmap WHERE discord = ?",
                   (discord,),
                   )
    return cursor.fetchone()


def update_mapping(discord: str, codeforces: str):
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


def reset_db_field(field: str):
    cursor.execute(f"UPDATE cfmap SET {field} = 0")
    conn.commit()


def set_problem(contest_id: str, idx: str):
    cursor.execute(
        """
        INSERT INTO problem(pk, contestID, idx)
        VALUES (?, ?, ?)
        ON CONFLICT(pk) DO UPDATE
        SET contestID = excluded.contestID,
            idx = excluded.idx
        """,
        (1, contest_id, idx),
    )
    conn.commit()


def get_problem() -> tuple | None:
    cursor.execute("SELECT * FROM problem WHERE pk = 1")
    return cursor.fetchone()[1:]


def increment_score(discord: str):
    cursor.execute(
        """
        UPDATE cfmap
        SET done_daily = 1,
            points = points + 1,
            mpoints = mpoints + 1
        WHERE discord = ?
        """,
        (discord,),
    )
    conn.commit()


def get_top_users(limit: int = 25, monthly: bool = False) -> list:
    pts = "mpoints" if monthly else "points"
    cursor.execute(
        f"""
        SELECT discord, {pts}
        FROM cfmap
        ORDER BY {pts} DESC
        LIMIT {limit}
        """)
    return cursor.fetchall()


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
    cursor.execute("INSERT INTO problem(pk, contestID, idx) VALUES (1, 'N/A', 'N/A')")
    conn.commit()
