from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/petjournal")
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
    title="PetCare Journal API",
    description="Backend API for PetCare Journal - Pet health tracking application",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None
)

# CORS middleware
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "https://petcarejournal.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pets = relationship("Pet", back_populates="owner")
    journal_entries = relationship("JournalEntry", back_populates="user")
    quick_logs = relationship("QuickLog", back_populates="user")

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
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="pets")
    journal_entries = relationship("JournalEntry", back_populates="pet")
    quick_logs = relationship("QuickLog", back_populates="pet")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    entry_type = Column(String, nullable=False)  # general, feeding, etc.
    date = Column(DateTime, nullable=False)
    time = Column(String, nullable=True)
    attachments = Column(Text, nullable=True)  # JSON string of file paths
    tags = Column(Text, nullable=True)  # JSON string of tags
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    pet = relationship("Pet", back_populates="quick_logs")
    user = relationship("User", back_populates="quick_logs")

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
    logger.info("Starting PetCare Journal API...")
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
    logger.info("Shutting down PetCare Journal API...")

# Authentication dependency (placeholder - will implement magic link auth)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    # TODO: Implement magic link authentication
    # For now, return a mock user
    user = db.query(User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user

# Routes
@app.get("/")
async def root():
    return {"message": "PetCare Journal API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

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
async def create_pet(pet: PetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_pet = Pet(**pet.dict(), owner_id=current_user.id)
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

@app.get("/pets/", response_model=List[PetResponse])
async def get_user_pets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pets = db.query(Pet).filter(Pet.owner_id == current_user.id).all()
    return pets

@app.get("/pets/{pet_id}", response_model=PetResponse)
async def get_pet(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    return pet

@app.put("/pets/{pet_id}", response_model=PetResponse)
async def update_pet(pet_id: int, pet_update: PetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
async def delete_pet(pet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    db.delete(pet)
    db.commit()
    return {"message": "Pet deleted successfully"}

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
