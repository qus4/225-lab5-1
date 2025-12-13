import sqlite3

DB_PATH = "/nfs/dev_contacts.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("[OK] Clearing test data only...")
c.execute("DELETE FROM contacts WHERE name LIKE 'TestUser_%'")

conn.commit()
conn.close()
print("[OK] Test data cleared.")
