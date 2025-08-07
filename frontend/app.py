import streamlit as st
import requests
from datetime import date
import pandas as pd

API_URL = "http://localhost:8000"  # Change to backend URL if deployed

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

st.title("💼 Budget Analyzer")

if "token" not in st.session_state:
    st.session_state.token = None

menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

if st.session_state.token is None:
    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            token = login(username, password)
            if token:
                st.session_state.token = token
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid login.")
    elif choice == "Sign Up":
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        if st.button("Sign Up"):
            if register(username, password):
                st.success("Account created! Please log in.")
            else:
                st.error("Username already exists.")
    st.stop()

st.sidebar.success("Logged in!")
if st.sidebar.button("Logout"):
    st.session_state.token = None
    st.experimental_rerun()

st.header("Add Entry")
entry_date = st.date_input("Date", value=date.today())
entry_type = st.radio("Type", ["Income", "Expense"])
entry_cat = st.text_input("Category")
entry_amt = st.number_input("Amount (₹)", min_value=0.0, step=0.01)
if st.button("Add Entry"):
    if add_entry(st.session_state.token, {"date": str(entry_date), "type": entry_type, "category": entry_cat, "amount": entry_amt}):
        st.success("Entry added.")
        st.experimental_rerun()
    else:
        st.error("Failed to add entry.")

st.header("Your Entries")
entries = get_entries(st.session_state.token)
if entries:
    df = pd.DataFrame(entries)
    st.dataframe(df)
    for idx, row in df.iterrows():
        if st.button(f"Delete {row['id']}", key=row['id']):
            delete_entry(st.session_state.token, row['id'])
            st.experimental_rerun()
else:
    st.info("No entries found.")