from sqlalchemy.orm import Session
from . import models, schemas, security


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        department_id=user.department_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user


def get_or_create_tags(db: Session, tag_names: list[str]) -> list[models.Tag]:
    tags = []
    for name in tag_names:
        tag = db.query(models.Tag).filter(models.Tag.name == name).first()
        if not tag:
            tag = models.Tag(name=name)
            db.add(tag)
        tags.append(tag)
    db.flush()
    return tags

def handle_document_upload(db: Session, title: str, user_id: int, file_path: str, tags: list[str]):
    db_document = db.query(models.Document).filter(models.Document.title == title).first()
    
    tag_objects = get_or_create_tags(db, tags)

    if db_document:
        # --- CASE 1: Document Exists - Then Create a new version ---
        print(f"--- Document '{title}' exists. Creating new version. ---")
        
        latest_version_number = db_document.latest_version.version_number if db_document.latest_version else 0
        new_version_number = latest_version_number + 1

        new_version = models.DocumentVersion(
            document_id=db_document.id,
            version_number=new_version_number,
            storage_path=file_path,
            uploaded_by_user_id=user_id
        )
        db.add(new_version)
        db.flush() 

        db_document.latest_version_id = new_version.id
        db_document.tags = tag_objects

        db.commit()
        db.refresh(db_document)
        return db_document

    else:
        # --- CASE 2: Document Does Not Exist - Then Create a new document and a first version ---
        print(f"--- Document '{title}' not found. Creating new document. ---")
        
        new_document = models.Document(
            title=title,
            created_by_user_id=user_id,
            tags=tag_objects
        )
        db.add(new_document)
        db.flush()

        first_version = models.DocumentVersion(
            document_id=new_document.id,
            version_number=1,
            storage_path=file_path,
            uploaded_by_user_id=user_id
        )
        db.add(first_version)
        db.flush()

        new_document.latest_version_id = first_version.id
        
        db.commit()
        db.refresh(new_document)
        return new_document
    
def search_documents(db: Session, query: str | None, tag_name: str | None):
    q = db.query(models.Document)

    if query:
        q = q.filter(models.Document.title.ilike(f"%{query}%"))

    if tag_name:
        q = q.join(models.Document.tags).filter(models.Tag.name == tag_name)

    return q.all()

def get_latest_document_version(db: Session, document_id: int):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document or not document.latest_version_id:
        return None
    
    return db.query(models.DocumentVersion).filter(models.DocumentVersion.id == document.latest_version_id).first()


def get_all_document_versions(db: Session, document_id: int):
    """Retrieves all historical versions of a document, newest first."""
    return db.query(models.DocumentVersion)\
             .filter(models.DocumentVersion.document_id == document_id)\
             .order_by(models.DocumentVersion.version_number.desc())\
             .all()


def seed_initial_data(db: Session):
    """
    Seeds the database with initial data if it's empty.
    """
    if db.query(models.Department).first() is None:
        print("--- Seeding initial departments ---")
        default_departments = [
            models.Department(name="Human Resources"),
            models.Department(name="Finance"),
            models.Department(name="IT"),
            models.Department(name="Engineering"),
            models.Department(name="Legal"),
        ]
        db.add_all(default_departments)
        db.commit()
        print("--- Seeding complete ---")
    else:
        print("--- Departments already exist, skipping seed ---")


def reset_database(db: Session):
    """
    Deletes all data from all tables in the correct order to avoid foreign key violations.
    """
    # 1. Break the circular dependency between documents and document_versions
    # We set latest_version_id to NULL before deleting the versions.
    db.query(models.Document).update({models.Document.latest_version_id: None})
    db.commit()

    # 2. Delete from the "many" side of relationships and join tables first
    db.query(models.document_tags).delete()
    db.query(models.document_permissions).delete()
    db.query(models.DocumentVersion).delete()
    
    # 3. Now we can delete the "one" side of the relationships
    db.query(models.Document).delete()
    db.query(models.Tag).delete()
    db.query(models.User).delete()
    
    # 4. Finally, delete the root-level tables
    db.query(models.Department).delete()
    
    db.commit()

    # 5. After deleting everything, re-seed the initial data (departments)
    # to return the database to a clean, usable state.
    print("--- Database has been reset. Re-seeding initial data. ---")
    seed_initial_data(db)

    return {"status": "success", "message": "Database has been reset and re-seeded."}


def get_departments(db: Session):
    return db.query(models.Department).all()