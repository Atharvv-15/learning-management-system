from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Lesson schemas
class LessonBase(BaseModel):
    title: str
    content: str
    video_url: Optional[str] = None
    duration: Optional[int] = None
    is_free: bool = False
    order_index: int

class LessonCreate(LessonBase):
    pass

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None
    is_free: Optional[bool] = None
    order_index: Optional[int] = None

class Lesson(LessonBase):
    id: int
    section_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

# Section schemas
class SectionBase(BaseModel):
    title: str
    order_index: int

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    title: Optional[str] = None
    order_index: Optional[int] = None

class Section(SectionBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    lessons: List[Lesson] = []

    class Config:
        orm_mode = True