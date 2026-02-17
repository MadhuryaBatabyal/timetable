import streamlit as st
import pandas as pd
import hashlib
import datetime as dt

st.set_page_config(page_title="College Timetable System", layout="wide")

# ---------------------- DEMO USERS (NO DB) ---------------------- #

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

DEMO_USERS = {
    # Admin (can also have timetable rows if you want)
    "admin": {
        "password": hash_pwd("admin"),
        "role": "Admin"
    },
    # Students – usernames must match timetable.csv
    "bsda2": {
        "password": hash_pwd("bsda2"),
        "role": "Student"
    },
    "bsda4": {
        "password": hash_pwd("bsda4"),
        "role": "Student"
    },
    "bsda6": {
        "password": hash_pwd("bsda6"),
        "role": "Student"
    },
}

# ---------------------- TIMETABLE HELPERS ---------------------- #

@st.cache_data
def load_timetable() -> pd.DataFrame:
    # timetable.csv must be in same folder as app.py
    return pd.read_csv("timetable.csv")

def get_today_name() -> str:
    days = [
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
    ]
    return days[dt.datetime.now().weekday()]

def show_today_timetable(username: str) -> None:
    tt = load_timetable()
    today = get_today_name()
    view = tt[(tt["username"] == username) & (tt["day"] == today)].copy()

    if view.empty:
        st.info("No classes scheduled for today 🎉")
        return

    view = view.sort_values("start_time")

    st.subheader(f"Today's Classes – {today}")
    st.dataframe(
        view[
            ["start_time", "end_time", "subject", "course", "room", "teacher"]
        ].rename(
            columns={
                "start_time": "Start",
                "end_time": "End",
                "subject": "Subject",
                "course": "Course",
                "room": "Room/Lab",
                "teacher": "Teacher",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

# ---------------------- SESSION STATE ---------------------- #

if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

# ---------------------- UI: TITLE ---------------------- #

st.title("🎓 College Timetable System")

# ---------------------- LOGIN PAGE ---------------------- #

if st.session_state.user is None:
    st.header("🔐 Login")

    col_info, col_form = st.columns([1, 2])

    with col_info:
        st.markdown("### Demo Accounts")
        st.code(
            "admin  / admin\n"
            "bsda2  / bsda2  (BSDA-II)\n"
            "bsda4  / bsda4  (BDSA-IV)\n"
            "bsda6  / bsda6  (BDSA-VI)"
        )

    with col_form:
        with st.form("login_form"):
            username = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            submitted = st.form_submit_button("🚀 Login")

            if submitted:
                if username in DEMO_USERS:
                    expected_hash = DEMO_USERS[username]["password"]
                    if hash_pwd(password) == expected_hash:
                        st.session_state.user = username
                        st.session_state.role = DEMO_USERS[username]["role"]
                        st.success(f"Welcome {username}!")
                        st.experimental_rerun()
                    else:
                        st.error("Wrong password")
                else:
                    st.error("Unknown user")

    st.stop()  # do not render dashboard until logged in

# ---------------------- DASHBOARD (AFTER LOGIN) ---------------------- #

current_user = st.session_state.user
current_role = st.session_state.role

# Sidebar info + logout
with st.sidebar:
    st.success(f"👋 {current_user} ({current_role})")
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.role = None
        st.experimental_rerun()

# Role-based views
if current_role == "Admin":
    st.header("🛠️ Admin Control Panel")
    show_today_timetable(current_user)

    col1, col2, col3 = st.columns(3)
    col1.metric("Timetables", 15)
    col2.metric("Events", 8)
    col3.metric("Users", 250)
    st.button("📊 Generate New Timetable", type="primary")

elif current_role == "Student":
    st.header("📅 Your Timetable")
    show_today_timetable(current_user)

else:  # you can later add a separate Faculty role
    st.header("📚 Dashboard")
    show_today_timetable(current_user)

# ---------------------- OPTIONAL: PDF DOWNLOAD ---------------------- #

st.markdown("---")
st.subheader("📄 Full Timetable (PDF)")
try:
    with open("DSA-TT-V5.pdf", "rb") as f:
        st.download_button(
            "Download Timetable PDF",
            f,
            file_name="Timetable_2025-26.pdf",
            mime="application/pdf",
        )
except FileNotFoundError:
    st.info("Upload DSA-TT-V5.pdf to enable PDF download.")
