from fastapi import FastAPI, HTTPException, Depends, status
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
import secrets
import hashlib
from dotenv import load_dotenv
import resend

# Load environment variables
load_dotenv()

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

class MagicLink(Base):
    __tablename__ = "magic_links"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

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

class MagicLinkRequest(BaseModel):
    email: EmailStr

class MagicLinkResponse(BaseModel):
    message: str
    email: str

class MagicLinkVerify(BaseModel):
    token: str

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# Magic Link Authentication Functions
def generate_magic_link_token() -> str:
    """Generate a secure random token for magic link"""
    return secrets.token_urlsafe(32)

def send_magic_link_email(email: str, token: str) -> bool:
    """Send magic link email using Resend"""
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        magic_link_url = f"{frontend_url}/auth/verify?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Sign in to Crittr</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0ea5e9, #22c55e); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #0ea5e9; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🐾 Welcome to Crittr!</h1>
                    <p>Your pet's health journey starts here</p>
                </div>
                <div class="content">
                    <h2>Sign in to your account</h2>
                    <p>Click the button below to securely sign in to your Crittr account:</p>
                    <a href="{magic_link_url}" class="button">Sign In to Crittr</a>
                    <p><strong>This link expires in 15 minutes for security.</strong></p>
                    <p>If you didn't request this sign-in link, you can safely ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Crittr - The journaling and tracking app for pet parents</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        params = {
            "from": "Crittr <noreply@crittr.app>",
            "to": [email],
            "subject": "🐾 Sign in to Crittr",
            "html": html_content,
        }
        
        email = resend.Emails.send(params)
        logger.info(f"Magic link email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send magic link email: {e}")
        return False

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
    return {"message": "Crittr API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication routes
@app.post("/auth/magic-link", response_model=MagicLinkResponse)
async def send_magic_link(request: MagicLinkRequest, db: Session = Depends(get_db)):
    """Send a magic link to the user's email"""
    email = request.email.lower().strip()
    
    # Generate secure token
    token = generate_magic_link_token()
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Store magic link in database
    magic_link = MagicLink(
        email=email,
        token=token,
        expires_at=expires_at
    )
    db.add(magic_link)
    db.commit()
    
    # Send email
    email_sent = send_magic_link_email(email, token)
    
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send magic link email"
        )
    
    return MagicLinkResponse(
        message="Magic link sent successfully",
        email=email
    )

@app.post("/auth/verify-magic-link")
async def verify_magic_link(request: MagicLinkVerify, db: Session = Depends(get_db)):
    """Verify magic link token and authenticate user"""
    magic_link = db.query(MagicLink).filter(
        MagicLink.token == request.token,
        MagicLink.used == False,
        MagicLink.expires_at > datetime.utcnow()
    ).first()
    
    if not magic_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired magic link"
        )
    
    # Mark magic link as used
    magic_link.used = True
    db.commit()
    
    # Find or create user
    user = db.query(User).filter(User.email == magic_link.email).first()
    if not user:
        # Create new user
        user = User(email=magic_link.email, name=magic_link.email.split('@')[0])
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # TODO: Generate JWT token for session management
    return {
        "message": "Authentication successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }

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
