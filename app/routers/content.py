from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, database
from ..deps import get_current_user
from ..schemas import section as schemas

router = APIRouter(tags=["Course Content"])

# Section routes
@router.post("/courses/{course_id}/sections/", response_model=schemas.Section)
def create_section(
    course_id: int,
    section: schemas.SectionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify course exists and user has permission
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify this course")

    db_section = models.Section(**section.dict(), course_id=course_id)
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

@router.get("/courses/{course_id}/sections/", response_model=List[schemas.Section])
def get_course_sections(
    course_id: int,
    db: Session = Depends(database.get_db)
):
    sections = db.query(models.Section)\
        .filter(models.Section.course_id == course_id)\
        .order_by(models.Section.order_index)\
        .all()
    return sections

@router.put("/sections/{section_id}", response_model=schemas.Section)
def update_section(
    section_id: int,
    section_update: schemas.SectionUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not db_section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Check permissions
    course = db.query(models.Course).filter(models.Course.id == db_section.course_id).first()
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify this section")

    for key, value in section_update.dict(exclude_unset=True).items():
        setattr(db_section, key, value)
    
    db.commit()
    db.refresh(db_section)
    return db_section

# Lesson routes
@router.post("/sections/{section_id}/lessons/", response_model=schemas.Lesson)
def create_lesson(
    section_id: int,
    lesson: schemas.LessonCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify section exists and user has permission
    section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    course = db.query(models.Course).filter(models.Course.id == section.course_id).first()
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify this section")

    db_lesson = models.Lesson(**lesson.dict(), section_id=section_id)
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

@router.get("/sections/{section_id}/lessons/", response_model=List[schemas.Lesson])
def get_section_lessons(
    section_id: int,
    db: Session = Depends(database.get_db)
):
    lessons = db.query(models.Lesson)\
        .filter(models.Lesson.section_id == section_id)\
        .order_by(models.Lesson.order_index)\
        .all()
    return lessons

@router.get("/lessons/{lesson_id}", response_model=schemas.Lesson)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # If lesson is not free, verify user has access
    if not lesson.is_free:
        # Here you would check if the user is enrolled in the course
        # We'll implement this later with the enrollment system
        pass
    
    return lesson

@router.put("/lessons/{lesson_id}", response_model=schemas.Lesson)
def update_lesson(
    lesson_id: int,
    lesson_update: schemas.LessonUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check permissions through section and course
    section = db.query(models.Section).filter(models.Section.id == db_lesson.section_id).first()
    course = db.query(models.Course).filter(models.Course.id == section.course_id).first()
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify this lesson")

    for key, value in lesson_update.dict(exclude_unset=True).items():
        setattr(db_lesson, key, value)
    
    db.commit()
    db.refresh(db_lesson)
    return db_lesson