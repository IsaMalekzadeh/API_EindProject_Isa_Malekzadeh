from sqlalchemy.orm import Session
from models import User
import hashlib
import secrets

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user_email: str, user_password: str):
    salt = secrets.token_hex(32)
    hashed_password = hash_password(user_password, salt)
    db_user = User(email=user_email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def hash_password(password: str, salt: str):
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}.{hashed_password.hex()}"
