"""
Auth API routes

POST /auth/register  — create new user
POST /auth/login     — authenticate and get tokens
POST /auth/refresh   — get new access token using refresh token
POST /auth/logout    — invalidate refresh token (optional, for better security)
POST /auth/me        — return current authenticated user)
"""

import logging
from datetime import datetime, timezone
 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
 
from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.redis_client import (
    clear_failed_attempts,
    denylist_token,
    is_rate_limited,
    record_failed_attempt,
)
from app.schemas import (
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserPublic,
)
 
logger = logging.getLogger(__name__)
 
router = APIRouter(prefix="/auth", tags=["auth"])

# ── Request Models ─────────────────────────────────────────────────────────────── #
# POST /auth/register

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED, summary="Register a new user")
async def register(user_in: UserCreate, session: Session = Depends(get_db)) -> UserPublic:
    """
    Create a new user account.
    Validates input, checks for existing username, hashes password, and saves to DB.
    Returns public user data (without sensitive fields).
    """
    existing_user = session.exec(select(User).where(User.username == user_in.username)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    
    new_user = User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    logger.info("New user registered: id=%s", new_user.id)
    return new_user

# POST auth/login
@router.post("/login", response_model=TokenResponse, summary="Authenticate user and get tokens")
async def login(user_in: LoginRequest, session: Session = Depends(get_db)) -> TokenResponse:

    auth_error = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid username or password",
        headers = {"WWW-Authenticate": "Bearer"},
    )

    rate_limit_error = HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many failed login attempts. Please try again later.",
    )

    if is_rate_limited(user_in.username):
        logger.warning("Rate limit hit for username: %s", user_in.username)
        raise rate_limit_error

    user = session.exec(select(User).where(User.username == user_in.username.lower())).first()
    if user is None:
        record_failed_attempt(user_in.username)
        raise auth_error

    if not user.is_active():
        raise auth_error

    if not verify_password(user_in.password, user.hashed_password):
        count = record_failed_attempt(user_in.username)
        logger.warning("Failed login attempt for user id=%s (%s/%s)", user.id, count, 5)
        raise auth_error

    clear_failed_attempts(user_in.username)

    user.last_login_at = datetime.now(timezone.utc)
    user.failed_login_attempts = 0
    session.add(user)
    session.commit()

    logger.info("User logged in: id=%s", user.id)

    return TokenResponse(access_token=create_access_token(user.id, user.role), refresh_token=create_refresh_token(user.id, user.role))

# POST auth/refresh
# This endpoint allows clients to obtain a new access token using a valid refresh token.
@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token using Refresh Token")
async def refresh_token(body: RefreshTokenRequest, session: Session = Depends(get_db)) -> TokenResponse:
    payload = decode_token(body.refresh_token, expected_type="refresh")
    user = session.get(User, int(payload.sub))
    if user is None or not user.is_active():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user.id, user.role), refresh_token=create_refresh_token(user.id, user.role))


# GET auth/me
# This endpoint returns the current authenticated user's information, allowing clients to verify their authentication status and retrieve user details.
@router.get("/me", response_model=UserPublic, summary="Get current authenticated user")
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

# POST auth/logout
# This endpoint allows clients to invalidate their refresh token, effectively logging out the user from that session.
@router.post("/logout", response_model=MessageResponse, summary="Logout by revoking the current session")
async def logout(current_user: User = Depends(get_current_user)) -> MessageResponse:
    ttl = settings.jwt_access_token_expire_minutes * 60
    denylist_token(str(current_user.id), ttl_seconds=ttl)
    logger.info("User logged out: id=%s", current_user.id)
    return MessageResponse(message="Successfully logged out")

# Avoid circular import — import settings after router definition
from app.config import settings  # noqa: E402