'''models.py — Database table definitions using SQLModel.
 
SQLModel bridges SQLAlchemy (ORM) and Pydantic (validation).
A class with `table=True` creates/maps to a real PostgreSQL table.'''

from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    admin = "admin"
    operator = "operator"

class UserStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    # TO ADD IN FUTURE: inactive = "inactive"  # For soft-deleted accounts or those pending reactivation

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False, max_length=100)
    hashed_password: str = Field(max_length=128, nullable=False)
    role: UserRole = Field(default=UserRole.operator, nullable=False)
    status: UserStatus = Field(default=UserStatus.active, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    last_login_at: datetime | None = Field(default=None, nullable=True)
    # ── Brute-force tracking (DB audit trail) ─────────────────────────────── #
    # Redis handles the fast lockout path; these columns are the durable record.
    failed_login_attempts: int = Field(default=0, nullable=False)
    lockout_until: datetime | None = Field(default=None, nullable=True)

    def is_locked(self) -> bool:
        """Check if the user is currently locked out."""
        if self.lockout_until is None:
            return False
        return self.lockout_until > datetime.now(timezone.utc)

    def is_active(self) -> bool:
        """Check if the user is active."""
        return self.status == UserStatus.active    