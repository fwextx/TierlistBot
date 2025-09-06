import sqlite3

DB_NAME = "tester_roles.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS allowed_roles (
                role_id INTEGER PRIMARY KEY
            )
        """)
        conn.commit()

def add_role(role_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO allowed_roles (role_id) VALUES (?)", (role_id,))
        conn.commit()
    
def remove_role(role_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM allowed_roles WHERE role_id = ?", (role_id,))
        conn.commit()

def get_allowed_roles() -> list[int]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role_id FROM allowed_roles")
        rows = cursor.fetchall()
        return [row[0] for row in rows]