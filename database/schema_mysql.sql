-- ============================================================
-- ScamShield AI - MySQL Schema (OPTIONAL)
-- ============================================================
-- The project runs on SQLite out-of-the-box (zero setup).
-- Use this file only if you want to switch to MySQL for
-- production / deployment. Import with:
--   mysql -u root -p < schema_mysql.sql
-- Then update utils/db.py to use PyMySQL / mysql-connector-python
-- instead of sqlite3.
-- ============================================================

CREATE DATABASE IF NOT EXISTS scamshield_ai;
USE scamshield_ai;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS scan_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    input_type VARCHAR(20) NOT NULL,     -- sms | email | url | upi
    input_text TEXT NOT NULL,
    prediction VARCHAR(20) NOT NULL,     -- safe | suspicious | fraud
    confidence FLOAT,
    is_digital_arrest TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS scam_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    scam_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    contact_info VARCHAR(150),
    status VARCHAR(20) DEFAULT 'pending', -- pending | reviewed | resolved
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Default admin account (password: Admin@123, hashed at app-level on first run)
-- Seeding is handled automatically by utils/db.py -> init_db() when using SQLite.
-- For MySQL, insert an admin row manually or via the Flask shell after import.
