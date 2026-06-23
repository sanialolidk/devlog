from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from devlog.api.deps import get_db
from devlog.models import Session as SessionModel, Tag
from devlog.schemas import SessionCreate, SessionResponse, TagRequest

router = APIRouter()


@router.get("", response_model=List[SessionResponse])
def list_sessions(today: bool = False, all: bool = False, db: Session = Depends(get_db)):
    query = db.query(SessionModel).order_by(SessionModel.start_time.desc())
    if today:
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(SessionModel.start_time >= start_of_day)
    elif not all:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        query = query.filter(SessionModel.start_time >= week_ago)
    return query.all()


@router.post("", response_model=SessionResponse, status_code=201)
def start_session(body: SessionCreate, db: Session = Depends(get_db)):
    active = db.query(SessionModel).filter(SessionModel.end_time.is_(None)).first()
    if active:
        raise HTTPException(status_code=409, detail=f"Session already active: {active.description}")
    session = SessionModel(description=body.description)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}/stop", response_model=SessionResponse)
def stop_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.end_time:
        raise HTTPException(status_code=409, detail="Session already stopped")
    session.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/tags", response_model=SessionResponse)
def tag_session(session_id: int, body: TagRequest, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    for name in body.names:
        name = name.lower().strip()
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
        if tag not in session.tags:
            session.tags.append(tag)
    db.commit()
    db.refresh(session)
    return session
