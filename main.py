import os.path
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import crud
import models
import schemas
from database import engine, SessionLocal

if not os.path.exists('.\sqlitedb'):
    os.makedirs('.\sqlitedb')

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

SECRET_KEY = "Mashallah"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dependency for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer for token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return to_encode

# Dependency for token verification
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Existing code for drinks and stock

# GET endpoint to retrieve all drinks
@app.get("/drinks/", response_model=list[schemas.Drink])
def get_drinks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_drinks(db, skip=skip, limit=limit)

# GET endpoint to retrieve all stock
@app.get("/stock/", response_model=list[schemas.Stock])
def get_stock(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_stock(db, skip=skip, limit=limit)

# DELETE endpoint to delete a specific drink by ID
@app.delete("/drinks/{drink_id}")
def delete_drink_endpoint(drink_id: int, db: Session = Depends(get_db)):
    crud.delete_drink(db, drink_id)
    return {"message": "Drink deleted successfully"}

# POST endpoint to create a new drink
@app.post("/drinks/", response_model=schemas.Drink)
def create_drink(drink: schemas.DrinkCreate, db: Session = Depends(get_db)):
    return crud.create_drink(db, drink)

# POST endpoint to create a new stock
@app.post("/stock/{drink_id}", response_model=schemas.Stock)
def create_stock(drink_id: int, stock: schemas.StockCreate, db: Session = Depends(get_db)):
    return crud.create_stock(db, stock, drink_id)

# New code for user-related operations

# POST endpoint for user registration
@app.post("/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

# GET endpoint to retrieve a specific user by ID
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user(db, user_id)

# GET endpoint to retrieve the current user's own information
@app.get("/users/me", response_model=schemas.User)
def read_me(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, current_user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# PUT endpoint to update the current user's own information
@app.put("/users/me", response_model=schemas.User)
def update_me(updated_user: schemas.UserCreate, current_user: str = Depends(get_current_user),
              db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, current_user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user information
    user.username = updated_user.username
    user.email = updated_user.email
    user.password = pwd_context.hash(updated_user.password)

    db.commit()
    db.refresh(user)
    return user
