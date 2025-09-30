from pydantic import BaseModel
from typing import List, Optional
import datetime

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    class Config:
        orm_mode = True


class UserSummary(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        from_attributes = True


class DocumentVersion(BaseModel):
    id: int
    version_number: int
    created_at: datetime.datetime
    uploader: UserSummary 
    storage_path: str
    class Config:
        from_attributes = True

class Document(BaseModel):
    id: int
    title: str
    creator: UserSummary 
    tags: List[Tag] = []
    versions: List[DocumentVersion] = []
    class Config:
        from_attributes = True

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

class Department(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None