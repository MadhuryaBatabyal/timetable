import streamlit as st
import pandas as pd
import hashlib

# Hardcoded secure demo users (production: use Supabase/Firebase)
DEMO_USERS = {
    'admin': {'password': hashlib.sha256('admin'.encode()).hexdigest(), 'role': 'Admin'},
    'prof': {'password': hashlib.sha256('prof'.encode()).hexdigest(), 'role': 'Faculty'},
    'student': {'password': hashlib.sha256('student'.encode()).hexdigest(), 'role': 'Student'}
}

def get_hash(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

st.set_page_config(page_title="Timetable App", layout="wide")
st.title("🎓 College Timetable System")

# Session state
if 'role' not in st.session_state:
    st.session_state.role = None
    st.session_state.user = None

# Clean login form
if st.session_state.role is None:
    st.header("🔐 Welcome - Please Login")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### Demo Accounts")
        st.code("""
admin / admin
prof / prof  
student / student""")
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            col_a, col_b = st.columns([3,1])
            with col_b:
                submit = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submit and username in DEMO_USERS:
                if DEMO_USERS[username]['password'] == get_hash(password):
                    st.session_state.role = DEMO_USERS[username]['role']
                    st.session_state.user = username
                    st.success(f"✅ Welcome {username}!")
                    st.rerun()
                else:
                    st.error("❌ Wrong password")
            elif submit:
                st.error("❌ Unknown user")
else:
    # Role dashboards
    st.sidebar.success(f"👋 {st.session_state.user} ({st.session_state.role})")
    st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.update({'role': None, 'user': None}) or st.rerun())
    
    if st.session_state.role == 'Admin':
        st.header("🛠️ Admin Control Panel")
        col1, col2, col3 = st.columns(3)
        col1.metric("Timetables", 15)
        col2.metric("Events", 8)
        col3.metric("Users", 250)
        st.button("🔄 Generate New Timetable", type="primary")
        
    elif st.session_state.role == 'Faculty':
        st.header("📚 Faculty Schedule")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Today", 3)
            st.metric("This Week", 15)
        with col2:
            today_tt = pd.DataFrame({
                "09:00": "Data Science (BSC-A)",
                "11:00": "Machine Learning (BSC-B)", 
                "14:00": "Statistics (BSC-A)"
            }, index=["Class"]).T
            st.dataframe(today_tt, use_container_width=True)
    
    else:  # Student
        st.header("📅 Your Timetable - BSc Data Science 3rd Year")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        slots = ["09-10", "11-12", "14-15"]
        data = {day: [f"{sub} {room}" for sub, room in zip(["Maths A101", "DSA A102", "ML Lab1"], range(3))] for day in days}
        st.dataframe(pd.DataFrame(data, index=slots), use_container_width=True)
        
        col1, col2 = st.columns(2)
        col1.button("📱 Download PDF")
        col2.button("🔔 Notifications")

if __name__ == "__main__":
    st.caption("Built for Zeal College Timetable System [IJCRT25A4273]") [file:1]
