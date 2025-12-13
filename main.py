from flask import Flask, request, render_template, redirect, url_for, jsonify
import sqlite3
import os
import math

app = Flask(__name__)
app.secret_key = "dev-secret"

# -----------------------------
# Dynamic Database Path (DEV vs PROD)
# -----------------------------
DB_NAME = os.environ.get("DB_NAME", "contacts.db")   # e.g. dev_contacts.db / prod_contacts.db
DB_PATH = f"/nfs/{DB_NAME}"


# -----------------------------
# Ensure DB & Table Exist
# -----------------------------
def ensure_db():
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


# -----------------------------
# Health check
# -----------------------------
@app.route("/health")
def health():
    return {"status": "ok", "db": DB_PATH}, 200


# -----------------------------
# Main Page (GET + POST)
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    ensure_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ---------- POST: add / update / delete ----------
    if request.method == "POST":
        action = request.form.get("action")

        # DELETE
        if action == "delete":
            cid = request.form.get("contact_id")
            if cid:
                c.execute("DELETE FROM contacts WHERE id=?", (cid,))
                conn.commit()

        # UPDATE
        elif action == "update":
            cid = request.form.get("contact_id")
            name = request.form.get("name")
            phone = request.form.get("phone")
            if cid and name and phone:
                c.execute("UPDATE contacts SET name=?, phone=? WHERE id=?",
                          (name, phone, cid))
                conn.commit()

        # ADD
        else:
            name = request.form.get("name")
            phone = request.form.get("phone")
            if name and phone:
                c.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)",
                          (name, phone))
                conn.commit()

        conn.close()
        return redirect(url_for("index"))

    # ---------- GET: pagination ----------
    PER_PAGE = 10

    try:
        page = max(int(request.args.get("page", 1)), 1)
    except:
        page = 1

    offset = (page - 1) * PER_PAGE

    # Total count
    c.execute("SELECT COUNT(*) FROM contacts")
    total = c.fetchone()[0]

    # Fetch contacts for this page
    c.execute(
        "SELECT * FROM contacts ORDER BY id DESC LIMIT ? OFFSET ?",
        (PER_PAGE, offset)
    )
    contacts = c.fetchall()
    conn.close()

    # Pagination math
    pages = max(1, math.ceil(total / PER_PAGE))
    has_prev = page > 1
    has_next = page < pages

    start_page = max(1, page - 2)
    end_page = min(pages, page + 2)

    return render_template(
        "index.html",
        contacts=contacts,
        page=page,
        pages=pages,
        has_prev=has_prev,
        has_next=has_next,
        start_page=start_page,
        end_page=end_page,
        total=total
    )


# -----------------------------
# Debug route
# -----------------------------
@app.route("/debug")
def debug():
    return jsonify({
        "message": "App running",
        "database": DB_PATH
    })


# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    ensure_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
