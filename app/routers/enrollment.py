from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, database
from ..deps import get_current_user
from datetime import datetime
from typing import Optional
from ..schemas import enrollment as schemas

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("/", response_model=schemas.Enrollment)
def create_enrollment(
    enrollment: schemas.EnrollmentCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if course exists
    course = db.query(models.Course).filter(models.Course.id == enrollment.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user is already enrolled
    existing_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == current_user.id,
        models.Enrollment.course_id == enrollment.course_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=400,
            detail="Already enrolled in this course"
        )

    # Create new enrollment
    db_enrollment = models.Enrollment(
        user_id=current_user.id,
        course_id=enrollment.course_id
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@router.get("/my-courses", response_model=List[schemas.EnrollmentWithCourse])
def get_user_enrollments(
    status: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Enrollment).filter(models.Enrollment.user_id == current_user.id)
    
    if status:
        query = query.filter(models.Enrollment.status == status)
    
    return query.all()

@router.get("/course/{course_id}/students", response_model=List[schemas.EnrollmentWithUser])
def get_course_enrollments(
    course_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify if user is the course instructor or admin
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view course enrollments")

    enrollments = db.query(models.Enrollment)\
        .filter(models.Enrollment.course_id == course_id)\
        .all()
    return enrollments

@router.put("/{enrollment_id}", response_model=schemas.Enrollment)
def update_enrollment(
    enrollment_id: int,
    enrollment_update: schemas.EnrollmentUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Check if user owns this enrollment or is course instructor/admin
    course = db.query(models.Course).filter(models.Course.id == enrollment.course_id).first()
    if enrollment.user_id != current_user.id and course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this enrollment")

    # Update enrollment
    for key, value in enrollment_update.dict(exclude_unset=True).items():
        setattr(enrollment, key, value)
    
    # If status is changed to completed, set completed_at
    if enrollment_update.status == "completed":
        enrollment.completed_at = datetime.utcnow()

    enrollment.last_accessed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(enrollment)
    return enrollment

@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def drop_enrollment(
    enrollment_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Check if user owns this enrollment or is admin
    if enrollment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to drop this enrollment")

    # Set status to dropped instead of deleting
    enrollment.status = "dropped"
    db.commit()
    return

@router.post("/{enrollment_id}/update-progress", response_model=schemas.Enrollment)
def update_progress(
    enrollment_id: int,
    progress: float,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if progress < 0 or progress > 100:
        raise HTTPException(status_code=400, detail="Progress must be between 0 and 100")

    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    if enrollment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this enrollment")

    enrollment.progress = progress
    enrollment.last_accessed_at = datetime.utcnow()
    
    # Auto-complete if progress is 100%
    if progress == 100:
        enrollment.status = "completed"
        enrollment.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(enrollment)
    return enrollment