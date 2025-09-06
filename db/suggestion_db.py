import sqlite3

DB_NAME = "suggestion_ticket_roles.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestion_roles (
                role_id INTEGER PRIMARY KEY
            )
        """)
        conn.commit()

def add_suggestion_role(role_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO suggestion_roles (role_id) VALUES (?)", (role_id,))
        conn.commit()
    
def remove_suggestion_role(role_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM suggestion_roles WHERE role_id = ?", (role_id,))
        conn.commit()

def get_suggestion_roles() -> list[int]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role_id FROM suggestion_roles")
        rows = cursor.fetchall()
        return [row[0] for row in rows]