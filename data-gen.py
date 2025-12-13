import sqlite3
import os

DATABASE = '/nfs/demo.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_table():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        );
    ''')
    db.commit()
    db.close()
    print("[INIT] contacts table ensured.")

def generate_test_data(num_contacts):
    db = get_db()
    for i in range(num_contacts):
        name = f'Test Name {i}'
        phone = f'123-456-789{i}'
        db.execute('INSERT INTO contacts (name, phone) VALUES (?, ?)', (name, phone))
    db.commit()
    print(f"[OK] {num_contacts} test contacts added.")
    db.close()

if __name__ == '__main__':
    init_table()
    generate_test_data(25)

