from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import shutil
from contextlib import asynccontextmanager

from . import crud, models, schemas, security
from .database import SessionLocal, engine

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# TODO Seed DB Before Starting 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    db = SessionLocal()
    try:
        crud.seed_initial_data(db)
    finally:
        db.close()
    yield
    # Code below yield runs on shutdown (if any)

app = FastAPI(lifespan=lifespan)

# Add this middleware configuration
origins = [
    "http://localhost:5173", # The default port for Vite React app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. User Registration & Login ---

@app.post("/register/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/login/", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- 2. Upload Document ---

@app.post("/documents/upload/")
def upload_document(
    db: Session = Depends(get_db),
    title: str = Form(...),
    tags: str = Form(...), # e.g., "Finance,Legal,Report"
    file: UploadFile = File(...)
    # In a real app, you would get the current user from the token
    # current_user: schemas.User = Depends(get_current_user)
):
    # For POC, let's assume a user ID
    user_id = 1 

    # 1. Save the file locally (in production, upload to S3/GCS)
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Create document and version in DB
    tag_list = [t.strip() for t in tags.split(',')]
    document = crud.create_document(db, title=title, user_id=user_id, file_path=file_path, tags=tag_list)
    
    return {"filename": file.filename, "document_id": document.id, "title": document.title}


# --- 3. Search Documents ---

@app.get("/documents/search/", response_model=List[schemas.Document])
def search_documents(
    q: Optional[str] = None, # Search by title
    tag: Optional[str] = None, # Search by tag
    db: Session = Depends(get_db)
):
    documents = crud.search_documents(db, query=q, tag_name=tag)
    return documents


# --- 4. View/Download Document ---

from fastapi.responses import FileResponse

@app.get("/documents/{document_id}/download/")
def download_document(document_id: int, db: Session = Depends(get_db)):
    latest_version = crud.get_latest_document_version(db, document_id=document_id)
    if not latest_version:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = latest_version.storage_path
    # This assumes the file exists at the path. Add error handling for production.
    return FileResponse(path=file_path, filename=file_path.split('/')[-1])

# --- 5. Fetch Version History ---
@app.get("/documents/{document_id}/versions/", response_model=List[schemas.DocumentVersion])
def get_document_versions(document_id: int, db: Session = Depends(get_db)):
    versions = crud.get_all_document_versions(db, document_id=document_id)
    if not versions:
        raise HTTPException(status_code=404, detail="Document not found")
    return versions