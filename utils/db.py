"""
utils/db.py
-----------
Lightweight database layer.

By default this project uses SQLite (zero setup - perfect for a hackathon
demo / judges running it locally). The exact same schema is provided in
`database/schema_mysql.sql` if you prefer MySQL for production - simply
swap the connection logic in `get_db()` and install PyMySQL / mysql-connector.

Tables:
    users          -> registered users (+ is_admin flag)
    scan_history   -> every AI fraud-check result (for the Dashboard)
    scam_reports   -> user-submitted scam reports (for the Admin Panel)
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "scamshield.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Creates tables if they don't exist, and seeds a default admin account."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            input_type TEXT NOT NULL,          -- sms | email | url | upi
            input_text TEXT NOT NULL,
            prediction TEXT NOT NULL,          -- safe | suspicious | fraud
            confidence REAL,
            is_digital_arrest INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS scam_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            scam_type TEXT NOT NULL,
            description TEXT NOT NULL,
            contact_info TEXT,
            status TEXT DEFAULT 'pending',     -- pending | reviewed | resolved
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )
    conn.commit()

    # Seed one default admin account for demo purposes
    admin = cur.execute("SELECT * FROM users WHERE email = ?", ("admin@scamshield.ai",)).fetchone()
    if not admin:
        cur.execute(
            "INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
            ("Admin", "admin@scamshield.ai", generate_password_hash("Admin@123"), 1),
        )
        conn.commit()

    conn.close()
