import os

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import mailer
from auth import (
    authenticate_user,
    check_verification_code,
    create_access_token,
    get_current_user,
    get_user_by_email,
    set_verification_code,
)
from database import engine, get_db
from models import User
from schemas import ResendCode, Token, UserCreate, UserResponse, VerifyEmail
from security import hash_password

app = FastAPI()

# lets the frontend (served from a different origin) call the API from the browser
# comma-separated list in backend/.env, e.g. CORS_ORIGINS=http://localhost:5173,http://localhost:3000
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "CheatPeeper backend is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-check")
def database_check():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database()")
        )
        database_name = result.scalar_one()

    return {
        "status": "connected",
        "database": database_name
    }


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role="student",
    )
    code = set_verification_code(new_user)

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists"
        )

    mailer.send_verification_email(new_user.email, code)

    return new_user


@app.post("/auth/verify-email")
def verify_email(data: VerifyEmail, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)

    if user is None or user.is_verified or not check_verification_code(user, data.code):
        db.commit()  # saves the failed attempt
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code"
        )

    user.is_verified = True
    user.verification_code_hash = None
    db.commit()

    return {"detail": "Email verified"}


@app.post("/auth/resend-code")
def resend_code(data: ResendCode, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)

    if user is not None and not user.is_verified:
        code = set_verification_code(user)
        db.commit()
        mailer.send_verification_email(user.email, code)

    # same response either way so this can't be used to check which emails have accounts
    return {"detail": "If that account exists and isn't verified, a new code was sent"}


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form "username" field accepts either a username or an email
    user = authenticate_user(db, form_data.username, form_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )

    return Token(access_token=create_access_token(user.id))


# declared before /users/{user_id} so "me" isn't parsed as an id
@app.get("/users/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_user)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
