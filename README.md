# Budget Analysis App

## Features
- Secure registration/login (passwords hashed)
- Each user’s data is private and visible only to them
- Add/view/delete income and expense entries

## Tech Stack
- FastAPI backend (JWT, bcrypt, SQLAlchemy)
- SQLite database (private per user, upgradeable to PostgreSQL)
- Streamlit frontend (REST API)

## Running Locally

### Backend:
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

### Frontend:
cd frontend
pip install -r requirements.txt
streamlit run app.py
# My-Money-Maneger-
