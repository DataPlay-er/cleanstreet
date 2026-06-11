from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app.redis_client import is_token_denylisted
from app.auth import decode_token
from app.models import User, UserRole, UserStatus
from app.schemas import TokenPayload

#Toen Extractor
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_db)) -> User:
    token = credentials.credentials
    payload = decode_token(token, expected_type="access") 
    if is_token_denylisted(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = session.exec(select(User).where(User.id == int(payload.sub))).first()
    """Or: user_id = int(payload.sub)
    user = session.get(User, user_id)"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User Suspended",
        )
    return user

def require_operator(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.operator, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator access required",
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user