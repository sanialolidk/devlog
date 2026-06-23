from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from devlog.db import Base

# Many-to-many join table between sessions and tags
session_tags = Table(
    "session_tags",
    Base.metadata,
    Column("session_id", Integer, ForeignKey("sessions.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime, nullable=True)
    tags = relationship("Tag", secondary=session_tags, back_populates="sessions")

    @property
    def duration_minutes(self):
        if not self.end_time:
            return None
        delta = self.end_time - self.start_time
        return round(delta.total_seconds() / 60, 1)

    @property
    def is_active(self):
        return self.end_time is None


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    sessions = relationship("Session", secondary=session_tags, back_populates="tags")
