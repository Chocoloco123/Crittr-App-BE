from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import os
import logging
import hashlib
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/crittr")
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("ENVIRONMENT") == "development"
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create FastAPI app
app = FastAPI(
    title="Crittr API",
    description="Backend API for Crittr - The journaling and tracking app for pet parents",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None
)

# CORS middleware
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "https://crittr.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    email_verified = Column(DateTime, nullable=True)
    image = Column(String, nullable=True)
    
    # Relationships
    pets = relationship("Pet", back_populates="owner")
    journal_entries = relationship("JournalEntry", back_populates="user")
    quick_logs = relationship("QuickLog", back_populates="user")
    pet_photos = relationship("PetPhoto", back_populates="user")

class Pet(Base):
    __tablename__ = "pets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)  # dog, cat, bird, etc.
    breed = Column(String, nullable=True)
    sex = Column(String, nullable=True)  # male, female, unknown
    birth_date = Column(DateTime, nullable=True)
    weight = Column(Float, nullable=True)
    color = Column(String, nullable=True)
    microchip_id = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    image = Column(String, nullable=True)  # Main profile photo URL
    image_position = Column(JSON, nullable=True)  # Image positioning data {x: number, y: number}
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="pets")
    journal_entries = relationship("JournalEntry", back_populates="pet")
    quick_logs = relationship("QuickLog", back_populates="pet")
    pet_photos = relationship("PetPhoto", back_populates="pet")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    entry_type = Column(String, nullable=False)  # general, feeding, etc.
    date = Column(DateTime, nullable=False)
    time = Column(String, nullable=True)
    attachments = Column(ARRAY(String), nullable=True)  # Array of file paths
    tags = Column(ARRAY(String), nullable=True)  # Array of tags
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pet = relationship("Pet", back_populates="journal_entries")
    user = relationship("User", back_populates="journal_entries")

class QuickLog(Base):
    __tablename__ = "quick_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    activity = Column(String, nullable=False)  # feeding, water, walk, etc.
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    pet = relationship("Pet", back_populates="quick_logs")
    user = relationship("User", back_populates="quick_logs")

class PetPhoto(Base):
    __tablename__ = "pet_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=False)
    is_main_photo = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pet = relationship("Pet", back_populates="pet_photos")
    user = relationship("User", back_populates="pet_photos")


class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_admin: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PetCreate(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    sex: Optional[str] = None  # male, female, unknown
    birth_date: Optional[datetime] = None
    weight: Optional[float] = None
    color: Optional[str] = None
    microchip_id: Optional[str] = None
    avatar: Optional[str] = None
    image: Optional[str] = None
    image_position: Optional[dict] = None

class PetResponse(BaseModel):
    id: int
    name: str
    species: str
    breed: Optional[str]
    sex: Optional[str]
    birth_date: Optional[datetime]
    weight: Optional[float]
    color: Optional[str]
    microchip_id: Optional[str]
    avatar: Optional[str]
    image: Optional[str]
    image_position: Optional[dict]
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JournalEntryCreate(BaseModel):
    title: str
    content: str
    entry_type: str
    date: datetime
    time: Optional[str] = None
    attachments: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    pet_id: int

class JournalEntryResponse(BaseModel):
    id: int
    title: str
    content: str
    entry_type: str
    date: datetime
    time: Optional[str]
    attachments: Optional[List[str]]
    tags: Optional[List[str]]
    pet_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QuickLogCreate(BaseModel):
    activity: str
    notes: Optional[str] = None
    pet_id: int

class QuickLogResponse(BaseModel):
    id: int
    activity: str
    notes: Optional[str]
    timestamp: datetime
    pet_id: int
    user_id: int
    
    class Config:
        from_attributes = True

class PhotoAlbumCreate(BaseModel):
    name: str
    description: Optional[str] = None
    pet_id: int

class PhotoAlbumResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    pet_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PhotoCreate(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    caption: Optional[str] = None
    tags: Optional[List[str]] = None
    album_id: Optional[int] = None
    pet_id: int

class PhotoResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    width: Optional[int]
    height: Optional[int]
    caption: Optional[str]
    tags: Optional[List[str]]
    album_id: Optional[int]
    pet_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Chatbot models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    model_used: str


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Load knowledge base for chatbot
def load_knowledge_base():
    """Load the knowledge base from file"""
    try:
        with open("knowledge.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Knowledge file not found")
        return "Crittr is a pet care tracking application."
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
        return "Crittr is a pet care tracking application."

# Get knowledge base content
KNOWLEDGE_BASE = load_knowledge_base()

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Crittr API...")
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Crittr API...")



# Admin check function with enhanced security
def verify_admin_access(email: str, db: Session) -> bool:
    """
    Verify admin access with multiple security checks:
    1. Email exists in admin_users table
    2. Admin account is active
    3. Update login tracking
    """
    try:
        admin_user = db.query(AdminUser).filter(
            AdminUser.email == email,
            AdminUser.is_active == True
        ).first()
        
        if admin_user:
            # Update login tracking
            admin_user.last_login = datetime.utcnow()
            admin_user.login_count += 1
            db.commit()
            
            logger.info(f"Admin access granted to {email} (login #{admin_user.login_count})")
            return True
        else:
            logger.warning(f"Admin access denied for {email} - not found or inactive")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying admin access for {email}: {str(e)}")
        return False


# Legacy function for backward compatibility
def is_admin_user(email: str, db: Session) -> bool:
    """Legacy admin check - use verify_admin_access for new code"""
    return verify_admin_access(email, db)


# Authentication dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    # TODO: Implement JWT token verification from magic link
    # For now, return a mock user or create one if none exists
    user = db.query(User).first()
    if not user:
        # Create a default user for development
        user = User(email="demo@crittr.app", name="Demo User")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# Optional authentication dependency for development
def get_current_user_optional(db: Session = Depends(get_db)):
    """Optional authentication - returns a user if available, creates one if not"""
    user = db.query(User).first()
    if not user:
        # Create a default user for development
        user = User(email="demo@crittr.app", name="Demo User")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# Routes
@app.get("/")
async def root():
    return {
        "message": "Crittr API", 
        "version": "1.0.0",
        "description": "Backend API for Crittr - The journaling and tracking app for pet parents",
        "chatbot": {
            "endpoint": "/query",
            "method": "POST",
            "description": "AI-powered chatbot for answering questions about Crittr features",
            "example": {
                "request": {"query": "What features does Crittr offer?"},
                "response": {"response": "AI-generated response", "model_used": "gpt-4o-mini"}
            }
        },
        "docs": "/docs" if os.getenv("ENVIRONMENT") == "development" else "Not available in production"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/query", response_model=QueryResponse)
async def query_chatbot(request: QueryRequest):
    """Process user query and return AI response about Crittr features"""
    try:
        # Prepare the prompt with knowledge base context
        system_prompt = f"""You are a helpful AI assistant for Crittr, a pet care tracking application. 
        
Use the following information about Crittr to answer user questions accurately and helpfully:

{KNOWLEDGE_BASE}

Guidelines for responses:
1. Be friendly and helpful
2. Focus on Crittr's current features
3. If asked about features not available, use the response guidelines provided in the knowledge base
4. Keep responses concise but informative
5. Always be professional and encouraging

Answer the user's question based on the information provided above."""

        # Make API call to OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.query}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        logger.info(f"Chatbot query processed successfully: {request.query[:50]}...")
        
        return QueryResponse(
            response=ai_response,
            model_used="gpt-4o-mini"
        )
        
    except Exception as e:
        logger.error(f"Error processing chatbot query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

# Authentication routes


# User routes
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.delete("/users/me")
async def delete_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete the current user and all their data"""
    try:
        # Get user identification from headers
        user_id_header = request.headers.get("X-User-ID")
        user_email_header = request.headers.get("X-User-Email")
        
        if not user_id_header or not user_email_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing user identification headers"
            )
        
        # Find the user in the database
        current_user = db.query(User).filter(User.id == user_id_header).first()
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify email matches
        if current_user.email != user_email_header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email mismatch - cannot delete another user's account"
            )
        
        # Prevent deletion of demo user
        if current_user.email == "demo@crittr.app":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Demo user account cannot be deleted"
            )
        
        logger.info(f"User {current_user.email} (ID: {current_user.id}) is deleting their account")
        
        # Delete all user-related data (cascade delete should handle this)
        # But let's be explicit for safety
        
        # Delete pet photos
        db.query(PetPhoto).filter(PetPhoto.user_id == current_user.id).delete()
        
        # Delete quick logs
        db.query(QuickLog).filter(QuickLog.user_id == current_user.id).delete()
        
        # Delete journal entries
        db.query(JournalEntry).filter(JournalEntry.user_id == current_user.id).delete()
        
        # Delete pets (this will cascade to pet photos)
        db.query(Pet).filter(Pet.owner_id == current_user.id).delete()
        
        # Finally, delete the user
        db.delete(current_user)
        db.commit()
        
        return {"message": "User account and all associated data have been permanently deleted"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )

@app.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint to delete any user account"""
    # Enhanced admin verification with security checks
    if not verify_admin_access(current_user.email, db):
        logger.warning(f"Unauthorized admin access attempt by {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Find the user to delete
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deletion of demo user even by admin
    if user_to_delete.email == "demo@crittr.app":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo user account cannot be deleted"
        )
    
    try:
        logger.info(f"Admin {current_user.email} is deleting user {user_to_delete.email} (ID: {user_id})")
        
        # Delete all user-related data
        db.query(PetPhoto).filter(PetPhoto.user_id == user_to_delete.id).delete()
        db.query(QuickLog).filter(QuickLog.user_id == user_to_delete.id).delete()
        db.query(JournalEntry).filter(JournalEntry.user_id == user_to_delete.id).delete()
        db.query(Pet).filter(Pet.owner_id == user_to_delete.id).delete()
        
        # Delete the user
        db.delete(user_to_delete)
        db.commit()
        
        return {"message": f"User {user_to_delete.email} and all associated data have been permanently deleted by admin"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_id} by admin {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )

# Pet routes
@app.post("/pets/", response_model=PetResponse)
async def create_pet(pet: PetCreate, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    db_pet = Pet(**pet.dict(), owner_id=current_user.id)
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

@app.get("/pets/", response_model=List[PetResponse])
async def get_user_pets(current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    pets = db.query(Pet).filter(Pet.owner_id == current_user.id).all()
    return pets

@app.get("/pets/{pet_id}", response_model=PetResponse)
async def get_pet(pet_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    return pet

@app.put("/pets/{pet_id}", response_model=PetResponse)
async def update_pet(pet_id: int, pet_update: PetCreate, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    for field, value in pet_update.dict().items():
        setattr(pet, field, value)
    
    db.commit()
    db.refresh(pet)
    return pet

@app.delete("/pets/{pet_id}")
async def delete_pet(pet_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    db.delete(pet)
    db.commit()
    return {"message": "Pet deleted successfully"}

# Photo Album routes
@app.post("/photo-albums/", response_model=PhotoAlbumResponse)
async def create_photo_album(album: PhotoAlbumCreate, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    # Verify pet belongs to user
    pet = db.query(Pet).filter(Pet.id == album.pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    db_album = PhotoAlbum(**album.dict(), user_id=current_user.id)
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album

@app.get("/photo-albums/", response_model=List[PhotoAlbumResponse])
async def get_photo_albums(pet_id: Optional[int] = None, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    query = db.query(PhotoAlbum).join(Pet).filter(Pet.owner_id == current_user.id)
    
    if pet_id:
        query = query.filter(PhotoAlbum.pet_id == pet_id)
    
    albums = query.order_by(PhotoAlbum.created_at.desc()).all()
    return albums

@app.get("/photo-albums/{album_id}", response_model=PhotoAlbumResponse)
async def get_photo_album(album_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    album = db.query(PhotoAlbum).join(Pet).filter(
        PhotoAlbum.id == album_id,
        Pet.owner_id == current_user.id
    ).first()
    
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo album not found"
        )
    
    return album

@app.put("/photo-albums/{album_id}", response_model=PhotoAlbumResponse)
async def update_photo_album(album_id: int, album_update: PhotoAlbumCreate, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    album = db.query(PhotoAlbum).join(Pet).filter(
        PhotoAlbum.id == album_id,
        Pet.owner_id == current_user.id
    ).first()
    
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo album not found"
        )
    
    for field, value in album_update.dict().items():
        setattr(album, field, value)
    
    db.commit()
    db.refresh(album)
    return album

@app.delete("/photo-albums/{album_id}")
async def delete_photo_album(album_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    album = db.query(PhotoAlbum).join(Pet).filter(
        PhotoAlbum.id == album_id,
        Pet.owner_id == current_user.id
    ).first()
    
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo album not found"
        )
    
    db.delete(album)
    db.commit()
    return {"message": "Photo album deleted successfully"}

# Photo routes
@app.post("/photos/", response_model=PhotoResponse)
async def create_photo(photo: PhotoCreate, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    # Verify pet belongs to user
    pet = db.query(Pet).filter(Pet.id == photo.pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    # Verify album belongs to user if specified
    if photo.album_id:
        album = db.query(PhotoAlbum).join(Pet).filter(
            PhotoAlbum.id == photo.album_id,
            Pet.owner_id == current_user.id
        ).first()
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo album not found"
            )
    
    db_photo = Photo(**photo.dict(), user_id=current_user.id)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

@app.get("/photos/", response_model=List[PhotoResponse])
async def get_photos(pet_id: Optional[int] = None, album_id: Optional[int] = None, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    query = db.query(Photo).join(Pet).filter(Pet.owner_id == current_user.id)
    
    if pet_id:
        query = query.filter(Photo.pet_id == pet_id)
    
    if album_id:
        query = query.filter(Photo.album_id == album_id)
    
    photos = query.order_by(Photo.created_at.desc()).all()
    return photos

@app.get("/photos/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    photo = db.query(Photo).join(Pet).filter(
        Photo.id == photo_id,
        Pet.owner_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    return photo

@app.put("/photos/{photo_id}", response_model=PhotoResponse)
async def update_photo(photo_id: int, photo_update: PhotoCreate, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    photo = db.query(Photo).join(Pet).filter(
        Photo.id == photo_id,
        Pet.owner_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    for field, value in photo_update.dict().items():
        setattr(photo, field, value)
    
    db.commit()
    db.refresh(photo)
    return photo

@app.delete("/photos/{photo_id}")
async def delete_photo(photo_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    photo = db.query(Photo).join(Pet).filter(
        Photo.id == photo_id,
        Pet.owner_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    db.delete(photo)
    db.commit()
    return {"message": "Photo deleted successfully"}

# Journal Entry routes
@app.post("/journal-entries/", response_model=JournalEntryResponse)
async def create_journal_entry(entry: JournalEntryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify pet belongs to user
    pet = db.query(Pet).filter(Pet.id == entry.pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    db_entry = JournalEntry(**entry.dict(), user_id=current_user.id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.get("/journal-entries/", response_model=List[JournalEntryResponse])
async def get_journal_entries(pet_id: Optional[int] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(JournalEntry).join(Pet).filter(Pet.owner_id == current_user.id)
    
    if pet_id:
        query = query.filter(JournalEntry.pet_id == pet_id)
    
    entries = query.order_by(JournalEntry.date.desc()).all()
    return entries

@app.get("/journal-entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(JournalEntry).join(Pet).filter(
        JournalEntry.id == entry_id,
        Pet.owner_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    return entry

# Quick Log routes
@app.post("/quick-logs/", response_model=QuickLogResponse)
async def create_quick_log(log: QuickLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify pet belongs to user
    pet = db.query(Pet).filter(Pet.id == log.pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    db_log = QuickLog(**log.dict(), user_id=current_user.id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@app.get("/quick-logs/", response_model=List[QuickLogResponse])
async def get_quick_logs(pet_id: Optional[int] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(QuickLog).join(Pet).filter(Pet.owner_id == current_user.id)
    
    if pet_id:
        query = query.filter(QuickLog.pet_id == pet_id)
    
    logs = query.order_by(QuickLog.timestamp.desc()).all()
    return logs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
