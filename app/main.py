from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import auth, course, content, enrollment

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LMS API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers here later
app.include_router(auth.router)
app.include_router(course.router)
app.include_router(content.router)
app.include_router(enrollment.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to LMS API"}