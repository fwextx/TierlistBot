import sqlite3

DB_NAME = "autorole_roles.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auto_roles (
                guild_id INTERGER,
                role_id INTEGER,
                PRIMARY KEY (guild_id, role_id)
            )
        """)
        conn.commit()

def add_autorole_role(guild_id: int, role_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO auto_roles (guild_id, role_id) VALUES (?, ?)", (guild_id, role_id,))
        conn.commit()
    
def remove_autorole_role(guild_id: int, role_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM auto_roles WHERE guild_id = ? AMD role_id = ?", (guild_id, role_id,))
        conn.commit()

def get_autorole_roles(guild_id: int) -> list[int]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role_id FROM auto_roles WHERE guild_id = ?", (guild_id))
        rows = cursor.fetchall()
        return [row[0] for row in rows]