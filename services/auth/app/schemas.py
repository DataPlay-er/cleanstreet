'''
API request bodies and response shape

Build Pydantic models that defines exactly what the API expects to receive and send — this is the contract between your backend and frontend (or any API consumer):
- Request models: define the shape of incoming data (LoginRequest , UserCreate, TokenRequest).
- Response models: define the shape of outgoing data (TokenResponse).
Pydantic models also handle validation and serialization, ensuring that your API receives well-formed data and sends consistent responses.

'''

import re
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

from app.config import settings
from app.models import UserRole, UserStatus

# ── Request Models ─────────────────────────────────────────────────────────────── #

# password validation:

def validate_password(password: str) -> str:
    errors: list[str] = []
    if len(password) < settings.password_min_length:
        raise ValueError(f"Password must be at least {settings.password_min_length} characters long.")
    if settings.password_require_uppercase and not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if settings.password_require_digit and not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")
    if settings.password_require_special and not re.search(r"[!@#$%^&*()-+]", password):
        raise ValueError("Password must contain at least one special character.")
    if re.search(r"\s", password):
        raise ValueError("Password must not contain whitespace.")
    if errors:
        raise ValueError(f"Password must contain: {', '.join(errors)}.")

    return password

class UserCreate(BaseModel):
    """
    Body for POST /auth/register.
    Password is validated here — never reaches the DB raw.
    """
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or len(v) < 3 or len(v) > 100:
            raise ValueError("Username too short or too long.")
        # Username must be alphanumeric plus @ and . for email-like usernames !!!(any other characters aside of letters are optional, so to lookk back at this condition)
        if not all(c.isalnum() or c in '@.' for c in v):
            raise ValueError("Username contains invalid characters.")
        return v.lower()

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        return validate_password(v)


class UserPublic(BaseModel):
    """
    Body for POST /auth/register.
    Public-facing user data.
    Never includes sensitive fields like hashed_password.
    """
    id: int
    username: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login_at: datetime | None

    model_config = {"from_attributes": True}  # allows .model_validate(orm_obj)

class LoginRequest(BaseModel):
    """
    Body for POST /auth/login.
    """
    username: str
    password: str

    @field_validator("username")    
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or len(v) < 3 or len(v) > 100:
            raise ValueError("Username too short or too long.")
        return v.lower()

# ── Response Models ────────────────────────────────────────────────────────────── #
# These define the shape of data sent back to the client. They can be used in FastAPI route decorators to automatically generate OpenAPI docs.
# For example, TokenResponse defines the structure of the JSON response when a client successfully logs in and receives JWT tokens.
# Using Pydantic models for responses ensures that your API consistently returns well-formed data, and it also provides clear documentation for API consumers.
# In this case, TokenResponse includes the access token, refresh token, and their expiration times, which are essential for the client to manage authentication state.
# By defining these models, you create a clear contract for what your API will return, making it easier for frontend developers to integrate with your backend and for tools like Swagger UI to generate interactive API documentation.
# In summary, request models validate incoming data, while response models define the structure of outgoing data, both contributing to a robust and well-documented API.
# ────────────────────────────────────────────────────────────────────────────── #
class TokenResponse(BaseModel):
    ''' Returned by /login and /refresh. '''
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")

class RefreshTokenRequest(BaseModel):
    """ Body for POST /auth/refresh. """
    refresh_token: str

class TokenPayload(BaseModel):
    """
    The decoded claims inside a JWT.
 
    sub:   subject — the user's id (as string, JWT standard)
    role:  user role — embedded so protected routes don't need a DB hit
    type:  "access" | "refresh" — prevents using a refresh token as access token
    exp:   expiry timestamp (handled by python-jose automatically)
    """
    sub: str                          # user id
    role: UserRole
    type: str                         # "access" or "refresh"

class MessageResponse(BaseModel):
    # A simple response model for endpoints that just return a message (e.g., logout confirmation).
    message: str    
