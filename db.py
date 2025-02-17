import sqlite3


def query_data(query: str, data=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    if data is not None:
        cursor.execute(query, data)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result


query_data("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        second_name TEXT,
        role TEXT NOT NULL,
        state TEXT NOT NULL
    );
""")
