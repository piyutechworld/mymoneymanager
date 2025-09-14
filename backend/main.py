from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models
import schemas
import database
import auth
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to your Streamlit URL in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    user = db.query(models.User).filter(models.User.username == payload['sub']).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(f"Attempting to register user: {user.username}")
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    print(f"Existing user: {existing_user}")
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists. If you forgot your password, use the 'Forget Password' option.")
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, password_hash=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print(f"User registered: {db_user.username}")
    return {"msg": "User registered"}

@app.post("/forget-password")
def forget_password(payload: dict, db: Session = Depends(get_db)):
    print(f"Forget password request for username: {payload.get('username')}")
    username = payload.get("username")
    if not username:
        print("No username provided.")
        raise HTTPException(status_code=400, detail="Username required")
    user = db.query(models.User).filter(models.User.username == username).first()
    print(f"User found for password reset: {user}")
    if not user:
        print("User not found for password reset.")
        raise HTTPException(status_code=404, detail="User not found")
    # Here you would send a password reset email or token
    # For demo, just return a message
    print(f"Password reset instructions sent for user: {username}")
    return {"msg": "Password reset instructions sent to your email (feature to be implemented)"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Login attempt for user: {form_data.username}")
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    print(f"User found: {user}")
    if not user:
        print("User not found.")
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        print("Incorrect password.")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    print(f"Login successful for user: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/entries/", response_model=schemas.Entry)
def create_entry(entry: schemas.EntryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_entry = models.Entry(**entry.dict(), user_id=current_user.id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.get("/entries/", response_model=list[schemas.Entry])
def read_entries(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Entry).filter(models.Entry.user_id == current_user.id).all()

@app.delete("/entries/{entry_id}")
def delete_entry(entry_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_entry = db.query(models.Entry).filter(models.Entry.id == entry_id, models.Entry.user_id == current_user.id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(db_entry)
    db.commit()
    return {"msg": "Entry deleted"}
