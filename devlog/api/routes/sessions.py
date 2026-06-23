from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from devlog.api.deps import get_db
from devlog.api.limiter import limiter
from devlog.api import cache
from devlog.models import Session as SessionModel, Tag
from devlog.schemas import SessionCreate, SessionResponse, TagRequest

router = APIRouter()

_CACHE_KEY = "sessions:list"


@router.get("", response_model=List[SessionResponse])
@limiter.limit("60/minute")
def list_sessions(
    request: Request,
    today: bool = False,
    all: bool = False,
    db: Session = Depends(get_db),
):
    # Only cache the default (last-7-days) view
    if not today and all:
        cached = cache.get(_CACHE_KEY + ":all")
        if cached is not None:
            return cached
    elif not today and not all:
        cached = cache.get(_CACHE_KEY + ":week")
        if cached is not None:
            return cached

    query = db.query(SessionModel).order_by(SessionModel.start_time.desc())
    if today:
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(SessionModel.start_time >= start_of_day)
    elif not all:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        query = query.filter(SessionModel.start_time >= week_ago)

    results = query.all()

    # Serialize via Pydantic so the cached value is JSON-safe
    serialized = [SessionResponse.model_validate(s).model_dump(mode="json") for s in results]

    if not today and all:
        cache.set(_CACHE_KEY + ":all", serialized)
    elif not today and not all:
        cache.set(_CACHE_KEY + ":week", serialized)

    return results


def _bust_cache():
    cache.delete(_CACHE_KEY + ":all")
    cache.delete(_CACHE_KEY + ":week")


@router.post("", response_model=SessionResponse, status_code=201)
@limiter.limit("10/minute")
def start_session(request: Request, body: SessionCreate, db: Session = Depends(get_db)):
    active = db.query(SessionModel).filter(SessionModel.end_time.is_(None)).first()
    if active:
        raise HTTPException(status_code=409, detail=f"Session already active: {active.description}")
    session = SessionModel(description=body.description)
    db.add(session)
    db.commit()
    db.refresh(session)
    _bust_cache()
    return session


@router.get("/{session_id}", response_model=SessionResponse)
@limiter.limit("60/minute")
def get_session(request: Request, session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}/stop", response_model=SessionResponse)
@limiter.limit("30/minute")
def stop_session(request: Request, session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.end_time:
        raise HTTPException(status_code=409, detail="Session already stopped")
    session.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    _bust_cache()
    return session


@router.post("/{session_id}/tags", response_model=SessionResponse)
@limiter.limit("30/minute")
def tag_session(request: Request, session_id: int, body: TagRequest, db: Session = Depends(get_db)):
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
    _bust_cache()
    return session
