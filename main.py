import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

# --------------------------------------------------
# Dynamic DB path (DEV / PROD 安全隔离)
# --------------------------------------------------
DB_NAME = os.environ.get("DB_NAME", "contacts.db")  # default fallback
DB_PATH = f"/nfs/{DB_NAME}"


# --------------------------------------------------
# Initialize DB
# --------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.route("/")
def index():
    return jsonify({
        "message": "Flask App Running",
        "database": DB_PATH
    })


@app.route("/contacts", methods=["GET"])
def get_contacts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM contacts")
    rows = c.fetchall()
    conn.close()

    result = [{"id": r[0], "name": r[1], "phone": r[2]} for r in rows]
    return jsonify(result)


@app.route("/contacts", methods=["POST"])
def add_contact():
    data = request.get_json()
    name = data.get("name")
    phone = data.get("phone")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()
    conn.close()

    return jsonify({"status": "OK", "message": "Contact added"}), 201


@app.route("/contacts/clear", methods=["POST"])
def clear_contacts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM contacts")
    conn.commit()
    conn.close()

    return jsonify({"status": "OK", "message": "All contacts deleted"})


# --------------------------------------------------
# App Start
# --------------------------------------------------
if __name__ == "__main__":
    print(f"[INIT] Using database: {DB_PATH}")
    init_db()
    app.run(host="0.0.0.0", port=5000)

@app.route("/")
def index():
    return jsonify({"message": "App running", "db": DB_PATH})

# ... (other routes)
