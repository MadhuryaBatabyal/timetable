import streamlit as st
import sqlite3
import hashlib
import pandas as pd

# Secure DB
@st.cache_resource
def get_connection():
    conn = sqlite3.connect('timetable_users.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (username TEXT PRIMARY KEY, password_hash TEXT, role TEXT)''')
    return conn

conn = get_connection()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

# Sidebar login
with st.sidebar:
    st.title("🔐 Auth")
    if not st.session_state.logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            result = conn.execute("SELECT role FROM users WHERE username=? AND password_hash=?",
                                 (username, hash_password(password))).fetchone()
            if result:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = result[0]
                st.success("✅ Logged in!")
                st.rerun()
            else:
                st.error("❌ Invalid")
        
        # Demo button
        if st.button("➕ Add Demo Users"):
            demos = [
                ('admin', hash_password('admin'), 'Admin'),
                ('prof', hash_password('prof'), 'Faculty'),
                ('student', hash_password('student'), 'Student')
            ]
            conn.executemany("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", demos)
            conn.commit()
            st.success("Demo users added!")
    else:
        st.success(f"Hi {st.session_state.username} ({st.session_state.role})")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()

# Main content (protected)
if st.session_state.logged_in:
    role = st.session_state.role
    
    if role == 'Admin':
        st.header("🛠️ Admin Dashboard")
        col1, col2 = st.columns(2)
        col1.button("📊 Generate Timetable")
        col2.button("📅 Manage Events")
        st.dataframe(pd.DataFrame({"Action": ["Create TT", "Reschedule", "Notifications"], 
                                  "Status": ["Ready", "Ready", "Ready"]}))
    
    elif role == 'Faculty':
        st.header("📚 Faculty View")
        st.metric("Today's Slots", 3)
        timetable = pd.DataFrame({
            "Time": ["9:00-10:00", "11:00-12:00", "14:00-15:00"],
            "Subject": ["Data Science", "Machine Learning", "Stats"],
            "Room": ["A-101", "A-102", "A-103"],
            "Students": [45, 40, 50]
        })
        st.dataframe(timetable)
    
    else:  # Student
        st.header("📅 Your Timetable")
        student_tt = pd.DataFrame({
            "Day": ["Monday", "Tuesday", "Wednesday"],
            "9-10AM": ["Maths", "ML", "Physics"],
            "11-12PM": ["DSA", "Stats", "Project"],
            "Room": ["B101", "B102", "Lab1"]
        })
        st.dataframe(student_tt)
        st.caption("💡 Updated: Feb 17, 2026")
        
else:
    st.info("👈 Sidebar: Add demo users (admin/admin, prof/prof, student/student) then login!")

conn.close()
