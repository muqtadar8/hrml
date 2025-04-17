import sqlite3
import streamlit as st

# Database initialization and functions
def init_db():
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    
    # Create tables with detailed schema
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE, 
                 password TEXT, 
                 is_admin INTEGER,
                 email TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 title TEXT, 
                 description TEXT, 
                 posted_by TEXT,
                 requirements TEXT,
                 salary_range TEXT,
                 location TEXT,
                 job_type TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 username TEXT, 
                 job_id INTEGER, 
                 resume TEXT, 
                 extracted_skills TEXT, 
                 extracted_exp TEXT, 
                 match_score REAL,
                 match_feedback TEXT,
                 application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 status TEXT DEFAULT 'Pending',
                 FOREIGN KEY(job_id) REFERENCES jobs(id),
                 FOREIGN KEY(username) REFERENCES users(username))''')
    
    conn.commit()
    return conn

# User management functions
def register_user(username, password, email, is_admin=False):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, is_admin, email) VALUES (?, ?, ?, ?)", 
                (username, password, int(is_admin), email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists

def login_user(username, password):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def get_user_info(username):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    return c.fetchone()

# Job management functions
def get_jobs():
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""SELECT id, title, description, posted_by, requirements, 
                salary_range, location, job_type, created_at FROM jobs 
                ORDER BY created_at DESC""")
    return c.fetchall()

def get_job_by_id(job_id):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""SELECT id, title, description, posted_by, requirements, 
                salary_range, location, job_type, created_at FROM jobs 
                WHERE id=?""", (job_id,))
    return c.fetchone()

def post_job(title, desc, posted_by, requirements, salary_range="", location="", job_type=""):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""INSERT INTO jobs 
                (title, description, posted_by, requirements, salary_range, location, job_type) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (title, desc, posted_by, requirements, salary_range, location, job_type))
    conn.commit()
    return c.lastrowid

def search_jobs(query):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    search_query = f"%{query}%"
    c.execute("""SELECT id, title, description, posted_by, requirements, 
                salary_range, location, job_type, created_at FROM jobs 
                WHERE title LIKE ? OR description LIKE ? OR requirements LIKE ?
                ORDER BY created_at DESC""", 
              (search_query, search_query, search_query))
    return c.fetchall()

# Application management functions
def apply_to_job(username, job_id, resume, skills, experience, match_score, match_feedback):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""INSERT INTO applications 
                (username, job_id, resume, extracted_skills, extracted_exp, match_score, match_feedback) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (username, job_id, resume, skills, experience, match_score, match_feedback))
    conn.commit()
    return c.lastrowid

def get_applications_by_job(job_id):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        SELECT a.id, a.username, j.title, a.extracted_skills, a.extracted_exp, a.match_score, 
               a.match_feedback, a.application_date, a.status
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE a.job_id = ?
        ORDER BY a.match_score DESC
    """, (job_id,))
    return c.fetchall()

def get_applications_by_employer(username):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        SELECT a.id, a.username, j.title, j.id, a.extracted_skills, a.extracted_exp, a.match_score, 
               a.match_feedback, a.application_date, a.status
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE j.posted_by = ?
        ORDER BY a.match_score DESC
    """, (username,))
    return c.fetchall()

def get_applications_by_user(username):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        SELECT a.id, j.title, j.posted_by, a.match_score, a.match_feedback, a.application_date, a.status, j.id
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE a.username = ?
        ORDER BY a.application_date DESC
    """, (username,))
    return c.fetchall()

def update_job_status(application_id, new_status):
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, application_id))
    conn.commit()