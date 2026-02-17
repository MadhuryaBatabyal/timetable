import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import os

# Use file-based DB with proper isolation
DB_PATH = 'users.db'

def get_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_users():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password_hash TEXT, role TEXT)''')
    # Always add demos (safe)
    demos = [
        ('admin', get_hash('admin'), 'Admin'),
        ('prof', get_hash('prof'), 'Faculty'),
        ('student', get_hash('student'), 'Student')
    ]
    c.executemany('INSERT OR IGNORE INTO users VALUES (?, ?, ?)', demos)
    conn.commit()
    conn.close()

# Init on start
if not os.path.exists(DB_PATH):
    init_users()

# Session
if 'role' not in st.session_state:
    st.session_state.role = None
    st.session_state.user = None

st.title("🎓 College Timetable System")

# Simple centered login (no sidebar issues)
if st.session_state.role is None:
    st.header("🔐 Login")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("👤 Username", placeholder="admin, prof, student")
        password = st.text_input("🔑 Password", type="password", placeholder="admin, prof, student")
        
        if st.button("🚀 Login", type="primary"):
            conn = sqlite3.connect(DB_PATH)
            result = conn.execute("SELECT role FROM users WHERE username=? AND password_hash=?",
                                 (username, get_hash(password))).fetchone()
            conn.close()
            
            if result:
                st.session_state.role = result[0]
                st.session_state.user = username
                st.success(f"✅ Welcome {username}!")
                st.rerun()
            else:
                st.error("❌ Wrong username/password")
    
    st.info("💡 Demo: admin/admin | prof/prof | student/student")
    
else:
    # Role-based dashboards
    role = st.session_state.role
    
    if role == 'Admin':
        st.header("🛠️ Admin Panel")
        col1, col2 = st.columns(2)
        col1.button("📊 Create Timetable", use_container_width=True)
        col2.button("📅 Reschedule Events", use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Feature": ["Timetable Gen", "Event Mgmt", "Notifications", "Permissions"],
            "Status": ["✅ Ready", "✅ Ready", "✅ Ready", "✅ Ready"]
        }))
    
    elif role == 'Faculty':
        st.header("📚 Faculty Dashboard")
        st.metric("Assigned Classes Today", 3)
        st.dataframe(pd.DataFrame({
            "Time": ["09:00-10:00", "11:00-12:00", "14:00-15:00"],
            "Subject": ["Data Science", "ML", "Statistics"],
            "Class": ["BSC-DS-A", "BSC-DS-B", "BSC-DS-A"],
            "Room": ["A101", "A102", "A103"]
        }), use_container_width=True)
    
    else:  # Student
        st.header("📖 My Timetable")
        st.caption("*BSc Data Science, 3rd Year*")
        tt_data = {
            "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "09:00-10:00": ["Maths", "ML", "Physics", "DSA", "Stats"],
            "11:00-12:00": ["DSA", "Stats", "Project", "Networks", "Elective"],
            "14:00-15:00": ["Lab", "Seminar", "Sports", "Lab", "Project"]
        }
        st.dataframe(pd.DataFrame(tt_data), use_container_width=True)
    
    # Logout
    col1, col2 = st.columns([3,1])
    col2.button("🚪 Logout", on_click=lambda: (setattr(st.session_state, 'role', None), setattr(st.session_state, 'user', None), st.rerun()))
