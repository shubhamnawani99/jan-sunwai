from datetime import datetime
import sqlite3

DB_NAME = "jan_sunwai.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grievances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_no TEXT,
            receipt_date TEXT,
            print_datetime TEXT,
            applicant_name TEXT,
            applicant_address TEXT,
            subject TEXT,
            marked_office TEXT,
            details TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_next_receipt_number(date_str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM grievances WHERE receipt_date = ?", (date_str,))
    count = cursor.fetchone()[0]
    conn.close()
    return f"{count + 1:02d}"

def update_grievance(record_id, applicant_name, applicant_address, subject, marked_office, details):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE grievances 
        SET applicant_name=?, applicant_address=?, subject=?, marked_office=?, details=?
        WHERE id=?
    """, (applicant_name, applicant_address, subject, marked_office, details, record_id))
    conn.commit()
    conn.close()

def delete_grievance(record_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grievances WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

def delete_all_grievances():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grievances")
    conn.commit()
    conn.close()