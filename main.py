import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

# -----------------------------
# Dynamic Database Path by ENV
# -----------------------------
DB_NAME = os.environ.get("DB_NAME", "contacts.db")   # default fallback
DB_PATH = f"/nfs/{DB_NAME}"

def init_db():
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

@app.route("/")
def index():
    return jsonify({"message": "App running", "db": DB_PATH})

# ... (other routes)
