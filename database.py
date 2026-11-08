"""Database layer for the Hospital Management System.
Uses SQLite (built into Python), so nothing extra needs to be installed."""
import sqlite3
from datetime import date

DB_NAME = "hospital.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL,
    age       INTEGER NOT NULL,
    gender    TEXT NOT NULL,
    phone     TEXT,
    address   TEXT,
    reg_date  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS doctors (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    specialization TEXT NOT NULL,
    phone          TEXT,
    fee            INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id  INTEGER NOT NULL,
    doctor_id   INTEGER NOT NULL,
    appt_date   TEXT NOT NULL,
    appt_time   TEXT NOT NULL,
    reason      TEXT,
    status      TEXT NOT NULL DEFAULT 'Scheduled',
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id)  REFERENCES doctors(id)
);

CREATE TABLE IF NOT EXISTS bills (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER NOT NULL,
    amount         INTEGER NOT NULL,
    paid           INTEGER NOT NULL DEFAULT 0,
    bill_date      TEXT NOT NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
);
"""


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row          # lets us read columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the tables if they do not exist yet."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def execute(sql, params=()):
    """Run INSERT / UPDATE / DELETE and return the new row id."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def query(sql, params=()):
    """Run a SELECT and return all rows."""
    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def load_sample_data():
    """Fill the database with made-up demo records (no real people)."""
    today = date.today().isoformat()
    patients = [
        ("Ayesha Khan", 28, "Female", "0300-1111111", "Haripur"),
        ("Ali Raza", 45, "Male", "0311-2222222", "Islamabad"),
        ("Sara Ahmed", 8, "Female", "0322-3333333", "Abbottabad"),
        ("Hamza Malik", 62, "Male", "0333-4444444", "Haripur"),
    ]
    for p in patients:
        execute("INSERT INTO patients (name, age, gender, phone, address, reg_date) "
                "VALUES (?, ?, ?, ?, ?, ?)", (*p, today))

    doctors = [
        ("Dr. Imran Shah", "General Medicine", "0345-5555555", 1500),
        ("Dr. Nadia Qureshi", "Pediatrics", "0346-6666666", 1800),
        ("Dr. Faisal Mehmood", "Cardiology", "0347-7777777", 3500),
    ]
    for d in doctors:
        execute("INSERT INTO doctors (name, specialization, phone, fee) VALUES (?, ?, ?, ?)", d)

    appointments = [
        (1, 1, "2026-12-01", "10:00", "Fever and cough", "Completed"),
        (2, 3, "2026-12-01", "11:30", "Chest pain checkup", "Scheduled"),
        (3, 2, "2026-12-02", "09:30", "Routine checkup", "Scheduled"),
        (4, 3, "2026-12-03", "12:00", "Blood pressure follow-up", "Completed"),
    ]
    for a in appointments:
        execute("INSERT INTO appointments (patient_id, doctor_id, appt_date, appt_time, reason, status) "
                "VALUES (?, ?, ?, ?, ?, ?)", a)

    execute("INSERT INTO bills (appointment_id, amount, paid, bill_date) VALUES (1, 1500, 1, ?)", (today,))
    execute("INSERT INTO bills (appointment_id, amount, paid, bill_date) VALUES (4, 4000, 0, ?)", (today,))
