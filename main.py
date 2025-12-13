from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import sqlite3
import os
import math

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# -----------------------------
# Dynamic Database Path by ENV
# -----------------------------
# DEV:  contacts_dev.db
# PROD: contacts_prod.db
DB_NAME = os.environ.get("DB_NAME", "contacts_dev.db")
DB_PATH = f"/nfs/{DB_NAME}"

PER_PAGE_DEFAULT = 10


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Ensure the database and table exist."""
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
    print(f"[INIT] Database ready at {DB_PATH}")


@app.route("/health")
def health():
    """Health check for Kubernetes."""
    return {"status": "ok", "db": DB_PATH}, 200


# -----------------------------
# Main Page with HTML UI
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    # Handle POST actions
    if request.method == "POST":
        action = request.form.get("action")

        # DELETE
        if action == "delete":
            contact_id = request.form.get("contact_id")
            if contact_id:
                db = get_db()
                db.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
                db.commit()
                db.close()
                flash("Contact deleted.", "success")
            return redirect(url_for("index"))

        # UPDATE
        if action == "update":
            contact_id = request.form.get("contact_id")
            name = request.form.get("name")
            phone = request.form.get("phone")
            if contact_id and name and phone:
                db = get_db()
                db.execute(
                    "UPDATE contacts SET name=?, phone=? WHERE id=?",
                    (name, phone, contact_id),
                )
                db.commit()
                db.close()
                flash("Contact updated.", "success")
            return redirect(url_for("index"))

        # ADD
        name = request.form.get("name")
        phone = request.form.get("phone")
        if name and phone:
            db = get_db()
            db.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
            db.commit()
            db.close()
            flash("Contact added!", "success")
        else:
            flash("Missing name or phone.", "danger")

        return redirect(url_for("index"))

    # -----------------------------
    # GET: Pagination
    # -----------------------------
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1

    try:
        per_page = max(int(request.args.get("per", PER_PAGE_DEFAULT)), 1)
    except ValueError:
        per_page = PER_PAGE_DEFAULT

    offset = (page - 1) * per_page

    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    rows = db.execute(
        "SELECT * FROM contacts ORDER BY id DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()
    db.close()

    pages = max(1, math.ceil(total / per_page))

    return render_template(
        "index.html",
        contacts=rows,
        page=page,
        pages=pages,
        per_page=per_page,
        total=total,
        has_prev=page > 1,
        has_next=page < pages,
        start_page=max(1, page - 2),
        end_page=min(pages, page + 2),
        db_path=DB_PATH
    )


# -----------------------------
# JSON Debug Route
# -----------------------------
@app.route("/info")
def info():
    return jsonify({
        "message": "Flask App Running (UI Mode)",
        "database": DB_PATH
    })


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
