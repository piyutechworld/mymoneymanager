import streamlit as st
import requests
from datetime import date
import pandas as pd

API_URL = "https://your-backend.onrender.com"  # Replace with your actual Render backend URL

def login(username, password):
    response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
    if response.ok:
        return response.json()['access_token']
    return None

def register(username, password):
    response = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
    return response.ok

def get_entries(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/entries/", headers=headers)
    return response.json() if response.ok else []

def add_entry(token, entry):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(f"{API_URL}/entries/", json=entry, headers=headers).ok

def delete_entry(token, entry_id):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.delete(f"{API_URL}/entries/{entry_id}", headers=headers).ok


st.markdown("<div class='custom-card'><h1 class='custom-title'>💼 Budget Analyzer</h1></div>", unsafe_allow_html=True)




# Further enhanced CSS for a modern, attractive UI
st.markdown("""
    <style>
    body, .main {background: linear-gradient(135deg, #f8ffae 0%, #43cea2 100%);}
    .stButton>button {
        background: linear-gradient(90deg, #ff7e5f 0%, #feb47b 100%);
        color: white;
        border-radius: 16px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 16px rgba(255,126,95,0.15);
        transition: background 0.3s, transform 0.2s;
        padding: 0.5em 2em;
        font-size: 1.1em;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
        color: #fff;
        transform: scale(1.05);
    }
    .stTextInput>div>input {
        border-radius: 12px;
        border: 2px solid #43cea2;
        background-color: #f7f9fa;
        font-size: 1.05em;
        padding: 0.4em;
    }
    .stRadio>div>label {
        font-weight: bold;
        color: #185a9d;
        font-size: 1.05em;
    }
    .stDataFrame {
        background-color: #fff;
        border-radius: 12px;
        border: 2px solid #feb47b;
        box-shadow: 0 2px 8px rgba(43,206,162,0.08);
    }
    .stSidebar {
        background: linear-gradient(180deg, #43cea2 0%, #185a9d 100%);
        color: #fff;
    }
    .custom-card {
        background: linear-gradient(135deg, #f8ffae 0%, #feb47b 100%);
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(255,126,95,0.12);
        padding: 2em 1.5em;
        margin-bottom: 2em;
    }
    .custom-title {
        color: #185a9d;
        font-size: 2.2em;
        font-weight: 700;
        text-shadow: 1px 2px 8px #feb47b44;
    }
    </style>
""", unsafe_allow_html=True)

if "token" not in st.session_state:
    st.session_state.token = None


with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/money.png", width=64)
    st.markdown("<h2 style='color:#fff; text-shadow: 1px 2px 8px #43cea244;'>MyMoneyManager</h2>", unsafe_allow_html=True)
    menu = ["Login", "Sign Up"]
    choice = st.selectbox("Menu", menu)


if st.session_state.token is None:
    st.markdown("<div class='custom-card'><h3 style='color:#ff7e5f;'>Welcome to MyMoneyManager!</h3><span style='color:#185a9d;'>Manage your budget with style. Please login or sign up to continue.</span></div>", unsafe_allow_html=True)
    if choice == "Login":
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        if st.button("Login", use_container_width=True):
            token = login(username, password)
            if token:
                st.session_state.token = token
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid login.")
    elif choice == "Sign Up":
        username = st.text_input("👤 Choose a username")
        password = st.text_input("🔒 Choose a password", type="password")
        if st.button("Sign Up", use_container_width=True):
            if register(username, password):
                st.success("Account created! Please log in.")
            else:
                st.error("Username already exists.")
    st.stop()

st.sidebar.success("Logged in!")


if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.token = None
    st.experimental_rerun()

st.header("Add Entry")


with st.expander("➕ Add New Entry", expanded=True):
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    entry_date = st.date_input("📅 Date", value=date.today())
    entry_type = st.radio("Type", ["Income", "Expense"], horizontal=True)
    entry_cat = st.text_input("🏷️ Category")
    entry_amt = st.number_input("💰 Amount (₹)", min_value=0.0, step=0.01)
    if st.button("Add Entry", use_container_width=True):
        if add_entry(st.session_state.token, {"date": str(entry_date), "type": entry_type, "category": entry_cat, "amount": entry_amt}):
            st.success("<span style='color:#43cea2;'>Entry added.</span>", unsafe_allow_html=True)
            st.experimental_rerun()
        else:
            st.error("<span style='color:#ff7e5f;'>Failed to add entry.</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.header("Your Entries")


entries = get_entries(st.session_state.token)
if entries:
    df = pd.DataFrame(entries)
    if not df.empty:
        df = df.sort_values(by=["date"], ascending=False)
        df["amount"] = df["amount"].apply(lambda x: f"₹{x:,.2f}")
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.dataframe(df.style.applymap(lambda v: 'color: #43cea2;' if 'Income' in str(v) else ('color: #ff7e5f;' if 'Expense' in str(v) else ''), subset=["type"]))
        st.markdown("<h4 style='color:#185a9d;'>Delete an Entry</h4>", unsafe_allow_html=True)
        for idx, row in df.iterrows():
            col1, col2, col3 = st.columns([6, 2, 2])
            with col1:
                st.write(f"{row['date']} | {row['type']} | {row['category']} | {row['amount']}")
            with col2:
                if st.button(f"🗑️ Delete", key=f"del_{row['id']}"):
                    delete_entry(st.session_state.token, row['id'])
                    st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("<span style='color:#feb47b;'>No entries found.</span>", unsafe_allow_html=True)
else:
    st.info("<span style='color:#feb47b;'>No entries found.</span>", unsafe_allow_html=True)