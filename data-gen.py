import sqlite3

DB_PATH = "/nfs/dev_contacts.db"   

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

    print("[OK] Clearing old TEST data...")
    c.execute("DELETE FROM contacts WHERE name LIKE 'TestUser_%'")

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
