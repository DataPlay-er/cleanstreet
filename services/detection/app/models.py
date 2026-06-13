'''ORM models for the detection service.
 
Two tables:
  • citizens          — face registry; each row is one enrolled person.
  • detection_events  — every processed frame that triggered a litter detection.

'''

from __future__ import annotations

from pgvector.sqlalchemy import Vector

import uuid
from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime, timezone

class Citizen(SQLModel, table=True):
    __tablename__ = "citizens"

    id: uuid.UUID() = Field(
        default_factory = uuid.uuid4,
        primary_key = True,
        index = True,
        nullable = False,
    )

    full_name: str = Field(max_length=255)
    national_id: int = Field(max_length=20, unique=True, index=True)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    embeddings : list[float] = Field(default=None, sa_column=Column(Vector(512), nullable=False))
    notes: Optional[str] = Field(default=None, max_length=255)


class DetectionEvent(SQLModel, table=True):
    __tablename__ = "detection_events"

    id: uuid.UUID() = Field(
        default_factory = uuid.uuid4,
        primary_key = True,
        index = True,
        nullable = False,
    )

    frame_path: str = Field(max_length=1024) # Path / URL of the source frame stored in MinIO.
    source_id: Optional[str] = Field(default=None, max_length=50, index=True)  # Originating camera / upload job identifier (free-form).

    litter_count: int = Field(default=0) # Number of litter objects detected in the frame.
    liiter_box: Optional[str] = Field(default=None)  # JSON-serialised list of bounding boxes: [[x1,y1,x2,y2,conf,cls], …]

    citizen_id: Optional[uuid.UUID] = Field(default=None, foreign_key="citizens.id", index=True) # FK to Citizen if a face was matched; NULL if no face or no match.
    face_similarity: Optional[float] = Field(default=None) # Raw cosine similarity score returned by pgvector (for audit).

    confidence: float = Field(default=0.0) # Raw cosine similarity score returned by pgvector (for audit).
    processing: Optional[float] = Field(default=None)  # Processing duration in milliseconds.

    status: str = Field(default="pending", max_length=50, index=True) # Lifecycle: pending → reviewed → notified | dismissed

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False, index=True)
