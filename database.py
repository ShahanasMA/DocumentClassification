import sqlite3

DB = "database.db"

def init_db():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # USERS TABLE (✅ added department)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        status TEXT,
        department TEXT
    )
    """)

    # DOCUMENTS TABLE
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

    # REVIEW REQUEST TABLE
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
