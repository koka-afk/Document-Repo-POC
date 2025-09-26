from pydantic import BaseModel
from typing import List, Optional
import datetime

# --- Tag Schemas ---
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    class Config:
        orm_mode = True

# --- Document Schemas ---
class DocumentVersion(BaseModel):
    id: int
    version_number: int
    created_at: datetime.datetime
    uploaded_by_user_id: int
    class Config:
        orm_mode = True

class Document(BaseModel):
    id: int
    title: str
    tags: List[Tag] = []
    versions: List[DocumentVersion] = []
    class Config:
        orm_mode = True

# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str
    department_id: int

class User(UserBase):
    id: int
    department_id: int
    class Config:
        orm_mode = True

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None