from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import shutil
from contextlib import asynccontextmanager

from jose import JWTError, jwt
from .schemas import TokenData

from . import crud, models, schemas, security
from .database import SessionLocal, engine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")

# Create DB tables
models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup to seed tge db
    db = SessionLocal()
    try:
        crud.seed_initial_data(db)
    finally:
        db.close()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


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


@app.post("/documents/upload/", response_model=schemas.Document)
def upload_document(
    db: Session = Depends(get_db),
    title: str = Form(...),
    tags: str = Form(...), 
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id

    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    tag_list = [t.strip() for t in tags.split(',')]
    document = crud.handle_document_upload(db, title=title, user_id=user_id, file_path=file_path, tags=tag_list)
    
    return document



@app.get("/documents/search/", response_model=List[schemas.Document])
def search_documents(
    q: Optional[str] = None, # Search by title
    tag: Optional[str] = None, # Search by tag
    db: Session = Depends(get_db)
):
    documents = crud.search_documents(db, query=q, tag_name=tag)
    return documents



from fastapi.responses import FileResponse

@app.get("/documents/{document_id}/download/")
def download_document(document_id: int, db: Session = Depends(get_db)):
    latest_version = crud.get_latest_document_version(db, document_id=document_id)
    if not latest_version:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = latest_version.storage_path
    return FileResponse(path=file_path, filename=file_path.split('/')[-1])

@app.get("/documents/{document_id}/versions/", response_model=List[schemas.DocumentVersion])
def get_document_versions(document_id: int, db: Session = Depends(get_db)):
    versions = crud.get_all_document_versions(db, document_id=document_id)
    if not versions:
        raise HTTPException(status_code=404, detail="Document not found")
    return versions


@app.post("/dev/reset-database/", status_code=status.HTTP_200_OK)
def reset_db(db: Session = Depends(get_db)):
    result = crud.reset_database(db)
    return result


@app.get("/departments/", response_model=list[schemas.Department])
def read_departments(db: Session = Depends(get_db)):
    departments = crud.get_departments(db)
    return departments