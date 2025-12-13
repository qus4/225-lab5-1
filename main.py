import os
import math
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# -----------------------------
# Dynamic database path for DEV & PROD
# -----------------------------
DB_NAME = os.environ.get("DB_NAME", "contacts.db")  
DB_PATH = f"/nfs/{DB_NAME}"

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()
    print(f"[INIT] Database initialized at {DB_PATH}")

@app.route("/health")
def health():
    return {"status": "ok", "db": DB_PATH}, 200


# -----------------------------
# MAIN PAGE (UI)
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    # POST handling
    if request.method == "POST":
        action = request.form.get("action")

        # DELETE
        if action == "delete":
            cid = request.form.get("contact_id")
            if cid:
                db = get_db()
                db.execute("DELETE FROM contacts WHERE id = ?", (cid,))
                db.commit()
                db.close()
            return redirect(url_for("index"))

        # UPDATE
        if action == "update":
            cid = request.form.get("contact_id")
            name = request.form.get("name")
            phone = request.form.get("phone")
            if cid and name and phone:
                db = get_db()
                db.execute(
                    "UPDATE contacts SET name=?, phone=? WHERE id=?",
                    (name, phone, cid)
                )
                db.commit()
                db.close()
            return redirect(url_for("index"))

        # ADD
        name = request.form.get("name")
        phone = request.form.get("phone")
        if name and phone:
            db = get_db()
            db.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
            db.commit()
            db.close()

        return redirect(url_for("index"))

    # GET (Pagination)
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except:
        page = 1

    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    contacts = db.execute(
        "SELECT * FROM contacts ORDER BY id DESC LIMIT ? OFFSET ?",
        (per_page, offset)
    ).fetchall()
    db.close()

    pages = max(1, math.ceil(total / per_page))

    return render_template(
        "index.html",
        contacts=contacts,
        page=page,
        pages=pages,
        per_page=per_page,
        total=total,
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

