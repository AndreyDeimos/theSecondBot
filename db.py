import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()


def query_data(query: str, data=None):
    if data is not None:
        cursor.execute(query, data)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    conn.commit()
    return result


query_data("""
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY,
        first_name TEXT,
        second_name TEXT,
        gender TEXT,
        role TEXT NOT NULL,
        state TEXT
    )
""")

query_data("""
    CREATE TABLE IF NOT EXISTS competitions (
        id INTEGER PRIMARY KEY,
        name TEXT,
        date TEXT,
        gender TEXT,
        required_participants INTEGER
    )
""")

query_data("""
    CREATE TABLE IF NOT EXISTS temporary_competitions (
        id INTEGER PRIMARY KEY, 
        name TEXT,
        date TEXT,
        gender TEXT,
        required_participants INTEGER,
        chat_id INTEGER
    )
""")

query_data("""
    CREATE TABLE IF NOT EXISTS registrations (
        chat_id INTEGER, 
        competition_id INTEGER
    )
""")

query_data("""
    CREATE TABLE IF NOT EXISTS logs (
        chat_id INTEGER, 
        object_id INTEGER,
        action_type TEXT,
        date TEXT
    )
""")
