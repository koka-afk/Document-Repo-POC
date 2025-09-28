from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from .database import Base
import datetime

document_tags = Table('document_tags', Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

document_permissions = Table('document_permissions', Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
    Column('department_id', Integer, ForeignKey('departments.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="Employee")
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department")

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    latest_version_id = Column(Integer, ForeignKey("document_versions.id"))
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User") 

    tags = relationship("Tag", secondary=document_tags, back_populates="documents")
    permissions = relationship("Department", secondary=document_permissions)
    versions = relationship(
        "DocumentVersion", 
        back_populates="document", 
        foreign_keys="[DocumentVersion.document_id]"
    )
    
   
    latest_version = relationship(
        "DocumentVersion", 
        foreign_keys=[latest_version_id],
        uselist=False,
        post_update=True 
    )

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    version_number = Column(Integer, nullable=False)
    storage_path = Column(String, nullable=False)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"))
    uploader = relationship("User") 

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    document = relationship(
            "Document", 
            back_populates="versions", 
            foreign_keys=[document_id]
        )
class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    documents = relationship("Document", secondary=document_tags, back_populates="tags")