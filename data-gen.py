import sqlite3
import os

# Dynamic DB path (same as main.py)
DB_NAME = os.environ.get("DB_NAME", "contacts.db")
DB_PATH = f"/nfs/{DB_NAME}"

def ensure_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("[INIT] contacts table ensured.")

def generate_test_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("[OK] Clearing old test data...")
    c.execute("DELETE FROM contacts")

    print("[OK] Inserting 20 test contacts...")

    for i in range(1, 21):
        c.execute(
            "INSERT INTO contacts (name, phone) VALUES (?, ?)",
            (f"TestUser_{i}", f"555-00{i:03d}")
        )

    conn.commit()
    conn.close()
    print("[OK] 20 test contacts added.")

if __name__ == "__main__":
    ensure_table()
    generate_test_data()
