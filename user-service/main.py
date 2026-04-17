from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt
import os
from jose import jwt
from datetime import datetime, timedelta

DATABASE_URL="sqlite:///./users.db"
engine=create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-local-dev-key")
ALGORITHM="HS256"

class User(Base):
    __tablename__="users"
    id=Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str
    
app= FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    #Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    #Create user

    db_user = User(email=user.email, hashed_password=hashed.decode('utf-8'))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created", "Email": user.email}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    #Find user
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    #Dheck password

    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        return HTTPException(status_code=401, detail="Invalid credentials")
    
    #Generate JWT

    token_data = {
        "sub": db_user.email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}