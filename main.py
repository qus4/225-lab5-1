import sqlite3
import os
import math
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = "dev"

# -------------------------
# Dynamic DB Name by ENV
# -------------------------
DB_NAME = os.environ.get("DB_NAME", "contacts.db")
DB_PATH = f"/nfs/{DB_NAME}"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"[INIT] Database initialized at {DB_PATH}")

@app.route("/health")
def health():
    return {"status": "ok"}, 200


# -------------------------
# FIXED "/" ROUTE
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    # -------------------------
    # POST: handle add/update/delete
    # -------------------------
    if request.method == "POST":
        action = request.form.get("action")

        # ADD
        if action == "add":
            name = request.form.get("name")
            phone = request.form.get("phone")
            if name and phone:
                conn = get_db()
                conn.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
                conn.commit()
                conn.close()
                flash("Contact added.", "success")
            return redirect(url_for("index"))

        # UPDATE
        if action == "update":
            cid = request.form.get("contact_id")
            name = request.form.get("name")
            phone = request.form.get("phone")
            conn = get_db()
            conn.execute("UPDATE contacts SET name=?, phone=? WHERE id=?", (name, phone, cid))
            conn.commit()
            conn.close()
            flash("Contact updated.", "success")
            return redirect(url_for("index"))

        # DELETE
        if action == "delete":
            cid = request.form.get("contact_id")
            conn = get_db()
            conn.execute("DELETE FROM contacts WHERE id=?", (cid,))
            conn.commit()
            conn.close()
            flash("Contact deleted.", "success")
            return redirect(url_for("index"))

    # -------------------------
    # GET: pagination + display
    # -------------------------
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except:
        page = 1

    try:
        per_page = max(int(request.args.get("per", 10)), 1)
    except:
        per_page = 10

    offset = (page - 1) * per_page

    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    contacts = conn.execute(
        "SELECT * FROM contacts ORDER BY id DESC LIMIT ? OFFSET ?",
        (per_page, offset)
    ).fetchall()
    conn.close()

    pages = max(1, math.ceil(total / per_page))
    start_page = max(1, page - 2)
    end_page = min(pages, page + 2)

    return render_template(
        "index.html",
        contacts=contacts,
        page=page,
        pages=pages,
        per_page=per_page,
        total=total,
        has_prev=page > 1,
        has_next=page < pages,
        start_page=start_page,
        end_page=end_page
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
