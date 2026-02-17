import streamlit as st
import streamlit_authenticator as stauth
import sqlite3
import hashlib
import yaml
from datetime import datetime
import pandas as pd

# 1. Setup DB (runs once)
@st.cache_resource
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, email TEXT, name TEXT, 
                  hashed_password TEXT, role TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 2. Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    exists = c.fetchone()
    conn.close()
    return exists

def add_user(username, email, name, password, role):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed = hash_password(password)
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
              (username, email, name, hashed, role, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# 3. Signup form
def signup():
    with st.form("signup"):
        st.subheader("📝 Sign Up")
        name = st.text_input("Name")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["Student", "Faculty", "Admin"])
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if password != confirm_password:
                st.error("Passwords don't match!")
            elif user_exists(username):
                st.error("Username exists!")
            else:
                add_user(username, email, name, password, role)
                st.success("Account created! Now login.")
                st.rerun()

# 4. Dynamic authenticator (reads from DB)
@st.cache_data(ttl=600)  # Refresh every 10 min
def get_credentials():
    conn = sqlite3.connect('users.db')
    df = pd.read_sql("SELECT username, name, email FROM users", conn)
    conn.close()
    config = {'credentials': {'usernames': {}}}
    for _, row in df.iterrows():
        config['credentials']['usernames'][row['username']] = {
            'name': row['name'], 'email': row['email']}
    return config

config = get_credentials()
authenticator = stauth.Authenticate(
    config['credentials'],
    'timetable_app', 'your_secret_key_abc123', 30
)

# 5. Main app
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

name, authentication_status, username = authenticator.login(location='main')

if auth_status:
    st.session_state.authenticated = True
    st.success(f'Welcome {name}!')
    
    # Get role from DB
    conn = sqlite3.connect('users.db')
    role = pd.read_sql("SELECT role FROM users WHERE username=?", conn, params=(username,)).iloc[0]['role']
    conn.close()
    
    if role == 'Admin':
        st.header("🛠️ Admin Panel")
        st.button("Create Timetable")
    elif role == 'Faculty':
        st.header("📚 Faculty Dashboard")
        st.dataframe(pd.DataFrame({'Today': ['9AM: DSA', '11AM: ML']}))
    else:  # Student
        st.header("📖 Your Timetable")
        st.dataframe(pd.DataFrame({'Mon': ['Math 9AM', 'DSA 11AM'], 'Tue': ['ML 9AM', 'Stats 11AM']}))
    
    authenticator.logout('Logout', 'main')
    
elif auth_status == False:
    st.error('Wrong credentials')
    signup()
else:
    signup()
