from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class EnrollmentBase(BaseModel):
    course_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[float] = None

class Enrollment(EnrollmentBase):
    id: int
    user_id: int
    progress: float
    status: str
    enrolled_at: datetime
    completed_at: Optional[datetime]
    last_accessed_at: datetime

    class Config:
        orm_mode = True

class EnrollmentWithCourse(Enrollment):
    from .course import Course
    course: Course

class EnrollmentWithUser(Enrollment):
    from .user import User
    user: User