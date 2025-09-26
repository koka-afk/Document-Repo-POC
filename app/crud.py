from sqlalchemy.orm import Session
from . import models, schemas, security

# --- User CRUD ---

def get_user_by_email(db: Session, email: str):
    """Fetches a single user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Creates a new user in the database with a hashed password."""
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
    """
    Authenticates a user.
    Returns the user object on success, None on failure.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user

# --- Document & Tag CRUD ---

def get_or_create_tags(db: Session, tag_names: list[str]) -> list[models.Tag]:
    """
    Finds existing tags or creates new ones for a given list of tag names.
    Returns a list of Tag ORM objects.
    """
    tags = []
    for name in tag_names:
        tag = db.query(models.Tag).filter(models.Tag.name == name).first()
        if not tag:
            tag = models.Tag(name=name)
            db.add(tag)
        tags.append(tag)
    # We might need to commit here if tags are new, let's flush to get IDs
    db.flush()
    return tags

def create_document(db: Session, title: str, user_id: int, file_path: str, tags: list[str]):
    """
    Creates a new document, its initial version, and associates tags.
    This is a transactional process.
    """
    # 1. Get or create the tag objects
    tag_objects = get_or_create_tags(db, tags)

    # 2. Create the main Document entry
    db_document = models.Document(
        title=title,
        created_by_user_id=user_id,
        tags=tag_objects  # SQLAlchemy handles the association
    )
    db.add(db_document)
    db.flush()  # Flush to assign an ID to db_document before using it

    # 3. Create the first DocumentVersion
    db_version = models.DocumentVersion(
        document_id=db_document.id,
        version_number=1,
        storage_path=file_path,
        uploaded_by_user_id=user_id
    )
    db.add(db_version)
    db.flush()  # Flush to assign an ID to db_version

    # 4. Link the document to its latest version
    db_document.latest_version_id = db_version.id

    db.commit()
    db.refresh(db_document)
    return db_document

def search_documents(db: Session, query: str | None, tag_name: str | None):
    """
    Searches for documents by title (case-insensitive) and/or by a specific tag.
    """
    # Start with a base query
    q = db.query(models.Document)

    if query:
        # Add a filter for the title using case-insensitive 'ilike'
        q = q.filter(models.Document.title.ilike(f"%{query}%"))

    if tag_name:
        # Add a join and filter for the tag name
        q = q.join(models.Document.tags).filter(models.Tag.name == tag_name)

    return q.all()

def get_latest_document_version(db: Session, document_id: int):
    """Retrieves the latest version of a specific document."""
    # Find the document to get its 'latest_version_id'
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document or not document.latest_version_id:
        return None
    
    # Return the version corresponding to that ID
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
    # Check if any departments already exist
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