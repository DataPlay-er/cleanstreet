'''
This file handles:
  1. Password hashing (bcrypt via passlib)
  2. JWT creation and verification (python-jose)
'''

from passlib.context import CryptContext
from app.config import settings
from app.models import UserRole
from app.schemas import TokenPayload
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(password: str) -> str:
    # bcrypt has a 72-byte limit, truncate if necessary
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(subject: str, role: UserRole, token_type: str, expires_delta: timedelta) -> str:
    payload = {
        "sub": str(subject),
        "role": role.value,        
        "type": token_type,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + expires_delta
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_access_token(user_id: int, role: UserRole) -> str:
    return create_token(
        subject= str(user_id),
        role=role,
        token_type="access",
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )

def create_refresh_token(user_id: int, role: UserRole) -> str:
    return create_token(
        subject=str(user_id),
        role=role,
        token_type="refresh",
        expires_delta=timedelta(days=settings.jwt_refresh_token_expire_days)
    )

def decode_token(token: str, expected_type: str= "access") -> TokenPayload:

    CredentialsError_handling = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise CredentialsError_handling

    sub = payload.get("sub")
    role_value = payload.get("role")
    token_type = payload.get("type")

    if sub is None or role_value is None or token_type is None:
        raise CredentialsError_handling

    if token_type != expected_type:
        raise CredentialsError_handling

    try:
        role = UserRole(role_value)
    except ValueError:
        raise CredentialsError_handling

    return TokenPayload(sub=sub, role=role, type=token_type)    