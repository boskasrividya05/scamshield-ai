"""
ScamShield AI - Flask Application
==================================
Economic Times AI Hackathon 2.0 - Phase 2
PS6: AI for Digital Public Safety - Defeating Counterfeiting, Fraud & Digital Arrest Scams

Run:
    python app.py
Then open http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

from utils.db import get_db, init_db
from utils import ml_utils

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# ---------------------------------------------------------------------------
# Initialise database (creates tables + seeds default admin on first run)
# ---------------------------------------------------------------------------
init_db()


# ---------------------------------------------------------------------------
# Auth helpers / decorators
# ---------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session or not session.get("is_admin"):
            flash("Admin access only.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("register"))

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("An account with this email already exists.", "danger")
            db.close()
            return redirect(url_for("register"))

        db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        db.commit()
        db.close()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["is_admin"] = bool(user["is_admin"])
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("admin_panel") if user["is_admin"] else url_for("dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Core feature pages (login required)
# ---------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    history = db.execute(
        "SELECT * FROM scan_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
        (session["user_id"],),
    ).fetchall()

    stats = db.execute(
        """SELECT prediction, COUNT(*) as count FROM scan_history
           WHERE user_id = ? GROUP BY prediction""",
        (session["user_id"],),
    ).fetchall()
    db.close()

    stats_dict = {"safe": 0, "suspicious": 0, "fraud": 0}
    for row in stats:
        stats_dict[row["prediction"]] = row["count"]

    return render_template("dashboard.html", history=history, stats=stats_dict)


@app.route("/detect")
@login_required
def detect():
    return render_template("detect.html")


@app.route("/digital-arrest")
@login_required
def digital_arrest():
    return render_template("digital_arrest.html")


@app.route("/upi-qr")
@login_required
def upi_qr():
    return render_template("upi_qr.html")


@app.route("/report", methods=["GET", "POST"])
@login_required
def report_scam():
    if request.method == "POST":
        scam_type = request.form.get("scam_type", "").strip()
        description = request.form.get("description", "").strip()
        contact_info = request.form.get("contact_info", "").strip()

        if not scam_type or not description:
            flash("Please fill in the scam type and description.", "danger")
            return redirect(url_for("report_scam"))

        db = get_db()
        db.execute(
            """INSERT INTO scam_reports (user_id, scam_type, description, contact_info)
               VALUES (?, ?, ?, ?)""",
            (session["user_id"], scam_type, description, contact_info),
        )
        db.commit()
        db.close()
        flash("Thank you! Your scam report has been submitted successfully.", "success")
        return redirect(url_for("report_scam"))

    return render_template("report.html")


@app.route("/safety-tips")
@login_required
def safety_tips():
    return render_template("safety_tips.html")


# ---------------------------------------------------------------------------
# Admin panel
# ---------------------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin_panel():
    db = get_db()
    reports = db.execute(
        """SELECT scam_reports.*, users.name as reporter_name, users.email as reporter_email
           FROM scam_reports LEFT JOIN users ON scam_reports.user_id = users.id
           ORDER BY scam_reports.created_at DESC"""
    ).fetchall()

    total_scans = db.execute("SELECT COUNT(*) as c FROM scan_history").fetchone()["c"]
    total_fraud = db.execute("SELECT COUNT(*) as c FROM scan_history WHERE prediction='fraud'").fetchone()["c"]
    total_users = db.execute("SELECT COUNT(*) as c FROM users WHERE is_admin=0").fetchone()["c"]
    total_reports = db.execute("SELECT COUNT(*) as c FROM scam_reports").fetchone()["c"]
    db.close()

    stats = {
        "total_scans": total_scans,
        "total_fraud": total_fraud,
        "total_users": total_users,
        "total_reports": total_reports,
    }
    return render_template("admin.html", reports=reports, stats=stats)


@app.route("/admin/update-status/<int:report_id>", methods=["POST"])
@admin_required
def update_report_status(report_id):
    new_status = request.form.get("status")
    db = get_db()
    db.execute("UPDATE scam_reports SET status = ? WHERE id = ?", (new_status, report_id))
    db.commit()
    db.close()
    flash("Report status updated.", "success")
    return redirect(url_for("admin_panel"))


# ---------------------------------------------------------------------------
# JSON API - AI detection endpoints (called via JavaScript / fetch)
# ---------------------------------------------------------------------------
@app.route("/api/detect", methods=["POST"])
@login_required
def api_detect():
    data = request.get_json(force=True)
    input_type = data.get("input_type", "sms")   # sms | email | url
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Please enter some text to analyze."}), 400

    if input_type == "url":
        result = ml_utils.classify_url(text)
    else:
        result = ml_utils.classify_text(text)

    db = get_db()
    db.execute(
        """INSERT INTO scan_history (user_id, input_type, input_text, prediction, confidence, is_digital_arrest)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (session["user_id"], input_type, text, result["prediction"], result["confidence"],
         int(result["is_digital_arrest"])),
    )
    db.commit()
    db.close()

    return jsonify(result)


@app.route("/api/check-upi", methods=["POST"])
@login_required
def api_check_upi():
    data = request.get_json(force=True)
    upi_id = (data.get("upi_id") or "").strip()
    if not upi_id:
        return jsonify({"error": "Please enter a UPI ID."}), 400

    result = ml_utils.check_upi_id(upi_id)

    db = get_db()
    db.execute(
        """INSERT INTO scan_history (user_id, input_type, input_text, prediction, confidence, is_digital_arrest)
           VALUES (?, ?, ?, ?, ?, 0)""",
        (session["user_id"], "upi", upi_id, result["prediction"], result["confidence"]),
    )
    db.commit()
    db.close()

    return jsonify(result)


@app.route("/api/dashboard-data")
@login_required
def api_dashboard_data():
    db = get_db()
    stats = db.execute(
        """SELECT prediction, COUNT(*) as count FROM scan_history
           WHERE user_id = ? GROUP BY prediction""",
        (session["user_id"],),
    ).fetchall()
    db.close()

    stats_dict = {"safe": 0, "suspicious": 0, "fraud": 0}
    for row in stats:
        stats_dict[row["prediction"]] = row["count"]
    return jsonify(stats_dict)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
