from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class SessionCreate(BaseModel):
    description: str


class TagRequest(BaseModel):
    names: List[str]


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[float]
    is_active: bool
    tags: List[TagResponse]
