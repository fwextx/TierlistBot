import sqlite3

DB_NAME = "region.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS region_roles (
                region_role_id INTEGER PRIMARY KEY,
                give_role_id INTEGER NOT NULL
            )
        """)
        conn.commit()

def add_region_role(region_role_id: int, give_role_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO region_roles (region_role_id, give_role_id)
            VALUES (?, ?)
        """, (region_role_id, give_role_id))
        conn.commit()

def remove_region_role(region_role_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM region_roles
            WHERE region_role_id = ?
        """, (region_role_id,))
        conn.commit()

def get_region_role() -> dict[int, int]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT region_role_id, give_role_id FROM region_roles")
        rows = cursor.fetchall()
        return {region: give for region, give in rows}