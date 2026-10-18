import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from database import get_db
from models import User
from security import hash_password, verify_password

# JWT settings, loaded from backend/.env (database.py already loads it)
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing from backend/.env")

VERIFICATION_CODE_EXPIRE_MINUTES = 10
MAX_VERIFICATION_ATTEMPTS = 5

# tells FastAPI (and the /docs page) where clients get a token from
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# looks up a user by username or email and checks the password
def authenticate_user(db: Session, login: str, password: str) -> User | None:
    user = db.scalars(
        select(User).where(or_(User.username == login, User.email == login.lower()))
    ).first()

    if user is None or not verify_password(password, user.password_hash):
        return None

    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()


# gives the user a fresh 6-digit code and returns it so it can be emailed
# only a hash is stored, same as passwords; caller commits
def set_verification_code(user: User) -> str:
    code = f"{secrets.randbelow(1_000_000):06d}"

    user.verification_code_hash = hash_password(code)
    user.verification_code_expires = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_CODE_EXPIRE_MINUTES)
    user.verification_attempts = 0

    return code


# checks a submitted code; wrong guesses count toward the attempt limit; caller commits
def check_verification_code(user: User, code: str) -> bool:
    if user.verification_code_hash is None or user.verification_attempts >= MAX_VERIFICATION_ATTEMPTS:
        return False

    expires = user.verification_code_expires
    if expires.tzinfo is None:  # SQLite drops the timezone
        expires = expires.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires:
        return False

    user.verification_attempts += 1
    return verify_password(code, user.verification_code_hash)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# dependency for protected routes: decodes the bearer token and returns its user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise credentials_exception

    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user
