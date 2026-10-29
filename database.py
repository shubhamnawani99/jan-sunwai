from datetime import datetime
import hashlib
from sqlalchemy import text
import streamlit as st

def get_connection():
    return st.connection("postgresql", type="sql")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    with conn.session as s:
        # Grievances table
        s.execute(text("""
            CREATE TABLE IF NOT EXISTS grievances (
                id SERIAL PRIMARY KEY,
                receipt_no TEXT,
                receipt_date TEXT,
                print_datetime TEXT,
                applicant_name TEXT,
                applicant_address TEXT,
                subject TEXT,
                marked_office TEXT,
                details TEXT
            )
        """))
        
        # Users table
        s.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'operator'
            )
        """))
        
        # Create a default admin user if no users exist (using Streamlit Secrets)
        result = s.execute(text("SELECT COUNT(*) FROM users")).fetchone()
        if result[0] == 0:
            admin_user = st.secrets.get("ADMIN_USERNAME")
            admin_pass = st.secrets.get("ADMIN_PASSWORD")
            
            default_pass_hashed = hash_password(admin_pass)
            s.execute(
                text("INSERT INTO users (username, password, role) VALUES (:username, :password, :role)"),
                {"username": admin_user, "password": default_pass_hashed, "role": "admin"}
            )
        s.commit()

def authenticate_user(username, password):
    conn = get_connection()
    hashed_pass = hash_password(password)
    query = "SELECT username, role FROM users WHERE username = :username AND password = :password"
    df = conn.query(query, params={"username": username, "password": hashed_pass}, ttl=0)
    if not df.empty:
        return (df.iloc[0]["username"], df.iloc[0]["role"])
    return None

def create_user(username, password, role="operator"):
    conn = get_connection()
    try:
        with conn.session as s:
            hashed_pass = hash_password(password)
            s.execute(
                text("INSERT INTO users (username, password, role) VALUES (:username, :password, :role)"),
                {"username": username, "password": hashed_pass, "role": role}
            )
            s.commit()
        return True, "User created successfully!"
    except Exception:
        return False, "Error: Username may already exist."

def get_next_receipt_number(date_str):
    conn = get_connection()
    query = "SELECT COUNT(*) FROM grievances WHERE receipt_date = :date_str"
    df = conn.query(query, params={"date_str": date_str}, ttl=0)
    count = df.iloc[0, 0] if not df.empty else 0
    return f"{count + 1:02d}"

def update_grievance(record_id, applicant_name, applicant_address, subject, marked_office, details):
    conn = get_connection()
    with conn.session as s:
        s.execute(text("""
            UPDATE grievances 
            SET applicant_name=:name, applicant_address=:addr, subject=:subj, marked_office=:office, details=:det
            WHERE id=:id
        """), {
            "name": applicant_name, "addr": applicant_address, 
            "subj": subject, "office": marked_office, 
            "det": details, "id": record_id
        })
        s.commit()

def delete_grievance(record_id):
    conn = get_connection()
    with conn.session as s:
        s.execute(text("DELETE FROM grievances WHERE id=:id"), {"id": record_id})
        s.commit()

def delete_all_grievances():
    conn = get_connection()
    with conn.session as s:
        s.execute(text("DELETE FROM grievances"))
        s.commit()