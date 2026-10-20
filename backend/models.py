from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(250))
    role: Mapped[str] = mapped_column(String(20), default="student")

    # email verification (set at signup, cleared once the code is entered)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_code_hash: Mapped[str | None] = mapped_column(String(250))
    verification_code_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_attempts: Mapped[int] = mapped_column(Integer, default=0)
