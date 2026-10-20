from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field


# stored lowercase so emails aren't case-sensitive
LowerEmail = Annotated[EmailStr, AfterValidator(str.lower)]


def require_ufl(email: str) -> str:
    if not email.endswith("@ufl.edu"):
        raise ValueError("must be a @ufl.edu email")
    return email


class UserCreate(BaseModel):
    # no "@" so a username can never match someone's email at login
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: Annotated[LowerEmail, AfterValidator(require_ufl)]
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VerifyEmail(BaseModel):
    email: LowerEmail
    code: str


class ResendCode(BaseModel):
    email: LowerEmail
