from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from devlog.api.deps import get_db
from devlog.api.limiter import limiter
from devlog.api.auth import get_current_user
from devlog.api import cache
from devlog.models import Session as SessionModel, Tag, User
from devlog.schemas import SessionCreate, SessionResponse, TagRequest

router = APIRouter()


def _cache_key(user_id: int, scope: str) -> str:
    return f"sessions:{user_id}:{scope}"


def _bust_cache(user_id: int) -> None:
    cache.delete(_cache_key(user_id, "all"))
    cache.delete(_cache_key(user_id, "week"))


@router.get("", response_model=List[SessionResponse])
@limiter.limit("60/minute")
def list_sessions(
    request: Request,
    today: bool = False,
    all: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not today:
        scope = "all" if all else "week"
        cached = cache.get(_cache_key(current_user.id, scope))
        if cached is not None:
            return cached

    query = (
        db.query(SessionModel)
        .filter(SessionModel.user_id == current_user.id)
        .order_by(SessionModel.start_time.desc())
    )
    if today:
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(SessionModel.start_time >= start_of_day)
    elif not all:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        query = query.filter(SessionModel.start_time >= week_ago)

    results = query.all()

    if not today:
        scope = "all" if all else "week"
        serialized = [SessionResponse.model_validate(s).model_dump(mode="json") for s in results]
        cache.set(_cache_key(current_user.id, scope), serialized)

    return results


@router.post("", response_model=SessionResponse, status_code=201)
@limiter.limit("10/minute")
def start_session(
    request: Request,
    body: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    active = (
        db.query(SessionModel)
        .filter(SessionModel.user_id == current_user.id, SessionModel.end_time.is_(None))
        .first()
    )
    if active:
        raise HTTPException(status_code=409, detail=f"Session already active: {active.description}")
    session = SessionModel(description=body.description, user_id=current_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    _bust_cache(current_user.id)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
@limiter.limit("60/minute")
def get_session(
    request: Request,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id, SessionModel.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}/stop", response_model=SessionResponse)
@limiter.limit("30/minute")
def stop_session(
    request: Request,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id, SessionModel.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.end_time:
        raise HTTPException(status_code=409, detail="Session already stopped")
    session.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    _bust_cache(current_user.id)
    return session


@router.post("/{session_id}/tags", response_model=SessionResponse)
@limiter.limit("30/minute")
def tag_session(
    request: Request,
    session_id: int,
    body: TagRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id, SessionModel.user_id == current_user.id)
        .first()
    )
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
    _bust_cache(current_user.id)
    return session
