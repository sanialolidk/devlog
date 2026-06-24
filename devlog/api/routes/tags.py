from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from devlog.api.deps import get_db
from devlog.api.auth import get_current_user
from devlog.models import Tag, User
from devlog.schemas import TagResponse

router = APIRouter()


@router.get("", response_model=List[TagResponse])
def list_tags(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Tag).order_by(Tag.name).all()
