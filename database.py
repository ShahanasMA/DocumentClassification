import sqlite3

DB = "database.db"

def get_db():
    return sqlite3.connect(DB)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        category TEXT,
        confidence REAL,
        preview TEXT,
        uploaded_by TEXT,
        upload_time TEXT,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS review_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        message TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()
