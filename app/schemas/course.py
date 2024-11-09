from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: str
    price: float
    level: str
    status: str = "draft"
    thumbnail_url: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    level: Optional[str] = None
    status: Optional[str] = None
    thumbnail_url: Optional[str] = None

class Course(CourseBase):
    id: int
    instructor_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True