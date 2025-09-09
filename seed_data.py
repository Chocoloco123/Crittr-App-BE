#!/usr/bin/env python3
"""
Seed script for PetCare Journal database
Creates sample users, pets, journal entries, and quick logs for demo purposes
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List
import random
import uuid

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import SessionLocal, User, Pet, JournalEntry, QuickLog, PetPhoto
from sqlalchemy.orm import Session

# Sample data
SAMPLE_USERS = [
    {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@example.com",
        "is_admin": False,
        "is_active": True
    },
    {
        "name": "Mike Chen",
        "email": "mike.chen@example.com", 
        "is_admin": False,
        "is_active": True
    },
    {
        "name": "Emily Rodriguez",
        "email": "emily.rodriguez@example.com",
        "is_admin": False,
        "is_active": True
    },
    {
        "name": "David Wilson",
        "email": "david.wilson@example.com",
        "is_admin": True,
        "is_active": True
    },
    {
        "name": "Lisa Thompson",
        "email": "lisa.thompson@example.com",
        "is_admin": False,
        "is_active": True
    }
]

SAMPLE_PETS = [
    # Sarah's pets
    {
        "name": "Buddy",
        "species": "dog",
        "breed": "Golden Retriever",
        "sex": "male",
        "birth_date": datetime.now() - timedelta(days=365*3),  # 3 years old
        "weight": 75.5,
        "color": "Golden",
        "microchip_id": "982000123456789",
        "avatar": None
    },
    {
        "name": "Whiskers",
        "species": "cat", 
        "breed": "Maine Coon",
        "sex": "female",
        "birth_date": datetime.now() - timedelta(days=365*2),  # 2 years old
        "weight": 12.3,
        "color": "Orange and White",
        "microchip_id": "982000987654321",
        "avatar": None
    },
    # Mike's pets
    {
        "name": "Luna",
        "species": "dog",
        "breed": "Border Collie",
        "sex": "female",
        "birth_date": datetime.now() - timedelta(days=365*4),  # 4 years old
        "weight": 45.2,
        "color": "Black and White",
        "microchip_id": "982000456789123",
        "avatar": None
    },
    # Emily's pets
    {
        "name": "Simba",
        "species": "cat",
        "breed": "Persian",
        "sex": "male",
        "birth_date": datetime.now() - timedelta(days=365*1),  # 1 year old
        "weight": 8.7,
        "color": "White",
        "microchip_id": "982000789123456",
        "avatar": None
    },
    {
        "name": "Nemo",
        "species": "fish",
        "breed": "Clownfish",
        "sex": "male",
        "birth_date": datetime.now() - timedelta(days=180),  # 6 months old
        "weight": 0.1,
        "color": "Orange and White",
        "microchip_id": None,
        "avatar": None
    },
    # David's pets
    {
        "name": "Max",
        "species": "dog",
        "breed": "German Shepherd",
        "sex": "male",
        "birth_date": datetime.now() - timedelta(days=365*5),  # 5 years old
        "weight": 85.0,
        "color": "Black and Tan",
        "microchip_id": "982000321654987",
        "avatar": None
    },
    # Lisa's pets
    {
        "name": "Bella",
        "species": "dog",
        "breed": "Labrador Mix",
        "sex": "female",
        "birth_date": datetime.now() - timedelta(days=365*2),  # 2 years old
        "weight": 55.8,
        "color": "Chocolate",
        "microchip_id": "982000147258369",
        "avatar": None
    },
    {
        "name": "Coco",
        "species": "bird",
        "breed": "Cockatiel",
        "sex": "female",
        "birth_date": datetime.now() - timedelta(days=365*1),  # 1 year old
        "weight": 0.3,
        "color": "Gray and Yellow",
        "microchip_id": None,
        "avatar": None
    }
]

# Sample journal entries
JOURNAL_ENTRY_TYPES = [
    "general", "feeding", "water", "walk", "potty", "symptoms", 
    "medication", "training", "grooming", "weight", "vet_visit"
]

SAMPLE_JOURNAL_ENTRIES = [
    {
        "title": "Morning Walk",
        "content": "Took Buddy for his usual morning walk around the neighborhood. He was very energetic today and met a few other dogs. Great exercise!",
        "entry_type": "walk",
        "time": "08:30"
    },
    {
        "title": "Vet Checkup",
        "content": "Annual checkup went well. Dr. Smith said Buddy is in excellent health. Weight is perfect at 75.5 lbs. Next appointment in 6 months.",
        "entry_type": "vet_visit",
        "time": "14:00"
    },
    {
        "title": "New Food Transition",
        "content": "Started transitioning Luna to the new premium dog food. Mixing 25% new food with 75% old food. She seems to like it so far.",
        "entry_type": "feeding",
        "time": "18:00"
    },
    {
        "title": "Training Session",
        "content": "Worked on 'stay' command with Max. He's getting much better at holding the position for longer periods. Very proud of his progress!",
        "entry_type": "training",
        "time": "16:30"
    },
    {
        "title": "Grooming Day",
        "content": "Gave Whiskers a thorough brushing. She shed quite a bit but looks much cleaner now. Used the new deshedding brush - works great!",
        "entry_type": "grooming",
        "time": "19:00"
    },
    {
        "title": "Weight Check",
        "content": "Monthly weight check for Simba. He's gained 0.2 lbs since last month, which is normal growth for his age. Currently 8.7 lbs.",
        "entry_type": "weight",
        "time": "10:00"
    },
    {
        "title": "Medication Given",
        "content": "Gave Bella her monthly heartworm prevention tablet. She took it easily with her dinner. No issues.",
        "entry_type": "medication",
        "time": "18:30"
    },
    {
        "title": "Behavioral Notes",
        "content": "Noticed Luna has been more anxious during thunderstorms. Will discuss with vet about possible anxiety management options.",
        "entry_type": "symptoms",
        "time": "20:15"
    },
    {
        "title": "Water Bowl Check",
        "content": "Refilled all water bowls and cleaned them thoroughly. Important to keep fresh water available, especially during hot weather.",
        "entry_type": "water",
        "time": "09:00"
    },
    {
        "title": "General Update",
        "content": "All pets are doing well today. Coco was particularly chatty this morning, singing his usual morning songs. Such a happy bird!",
        "entry_type": "general",
        "time": "07:00"
    }
]

SAMPLE_QUICK_LOGS = [
    {"activity": "feeding", "notes": "Breakfast - 1 cup kibble"},
    {"activity": "water", "notes": "Refilled water bowl"},
    {"activity": "walk", "notes": "30 minute walk around the park"},
    {"activity": "potty", "notes": "Successful bathroom break"},
    {"activity": "medication", "notes": "Heartworm prevention tablet"},
    {"activity": "grooming", "notes": "Quick brush and nail trim"},
    {"activity": "training", "notes": "10 minute training session"},
    {"activity": "weight", "notes": "Monthly weight check"},
    {"activity": "symptoms", "notes": "Monitoring energy levels"},
    {"activity": "feeding", "notes": "Dinner - 1.5 cups kibble"}
]

def create_sample_data(db: Session):
    """Create sample data in the database"""
    
    print("🌱 Starting to seed database...")
    
    # Create users
    users = []
    for user_data in SAMPLE_USERS:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"⚠️  User {user_data['email']} already exists, skipping...")
            users.append(existing_user)
            continue
            
        user = User(id=str(uuid.uuid4()), **user_data)
        db.add(user)
        users.append(user)
        print(f"✅ Created user: {user_data['name']} ({user_data['email']})")
    
    db.commit()
    
    # Create pets
    pets = []
    pet_index = 0
    
    # Assign all pets to demo user (ID '1')
    demo_user_id = '1'
    
    for pet_index in range(len(SAMPLE_PETS)):
        pet_data = SAMPLE_PETS[pet_index].copy()
        pet_data["owner_id"] = demo_user_id
        
        # Check if pet already exists
        existing_pet = db.query(Pet).filter(
            Pet.name == pet_data["name"],
            Pet.owner_id == demo_user_id
        ).first()
        
        if existing_pet:
            print(f"⚠️  Pet {pet_data['name']} for demo user already exists, skipping...")
            pets.append(existing_pet)
            continue
        
        pet = Pet(**pet_data)
        db.add(pet)
        pets.append(pet)
        print(f"✅ Created pet: {pet_data['name']} ({pet_data['species']}) for demo user")
    
    db.commit()
    
    # Create journal entries
    print("\n📝 Creating journal entries...")
    for i in range(50):  # Create 50 journal entries
        pet = random.choice(pets)
        
        # Get random journal entry template
        entry_template = random.choice(SAMPLE_JOURNAL_ENTRIES)
        
        # Create entry with random date in the last 30 days
        days_ago = random.randint(0, 30)
        entry_date = datetime.now() - timedelta(days=days_ago)
        
        # Random time if not specified
        if not entry_template.get("time"):
            hour = random.randint(6, 22)
            minute = random.randint(0, 59)
            entry_template["time"] = f"{hour:02d}:{minute:02d}"
        
        journal_entry = JournalEntry(
            title=entry_template["title"],
            content=entry_template["content"],
            entry_type=entry_template["entry_type"],
            date=entry_date,
            time=entry_template["time"],
            attachments=[],  # Empty array
            tags=random.sample(["health", "exercise", "nutrition", "behavior", "medical"], random.randint(1, 3)),  # Actual array
            pet_id=pet.id,
            user_id=demo_user_id
        )
        
        db.add(journal_entry)
    
    db.commit()
    print("✅ Created 50 journal entries")
    
    # Create quick logs
    print("\n⚡ Creating quick logs...")
    for i in range(100):  # Create 100 quick logs
        pet = random.choice(pets)
        
        # Get random quick log template
        log_template = random.choice(SAMPLE_QUICK_LOGS)
        
        # Create log with random timestamp in the last 7 days
        hours_ago = random.randint(0, 168)  # 7 days * 24 hours
        log_timestamp = datetime.now() - timedelta(hours=hours_ago)
        
        quick_log = QuickLog(
            activity=log_template["activity"],
            notes=log_template["notes"],
            timestamp=log_timestamp,
            pet_id=pet.id,
            user_id=demo_user_id
        )
        
        db.add(quick_log)
    
    db.commit()
    print("✅ Created 100 quick logs")
    
    # Create sample pet photos
    print("\n📸 Creating pet photos...")
    sample_photo_urls = [
        "https://images.unsplash.com/photo-1552053831-71594a27632d?w=400",  # Golden Retriever
        "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400",  # Cat
        "https://images.unsplash.com/photo-1551717743-49959800b1f6?w=400",  # Border Collie
        "https://images.unsplash.com/photo-1596854407944-bf87f6fdd49e?w=400",  # Persian Cat
        "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400",  # Fish
        "https://images.unsplash.com/photo-1583337130417-b6a253a1e9be?w=400",  # German Shepherd
        "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400",  # Labrador
        "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400",  # Bird
    ]
    
    photo_titles = [
        "Morning Playtime",
        "Nap Time",
        "Outdoor Adventure", 
        "Grooming Session",
        "Feeding Time",
        "Training Session",
        "Cuddle Time",
        "Exploring"
    ]
    
    for i in range(20):  # Create 20 sample photos
        pet = random.choice(pets)
        
        pet_photo = PetPhoto(
            title=random.choice(photo_titles),
            description=f"A lovely photo of {pet.name}",
            image_url=random.choice(sample_photo_urls),
            is_main_photo=(i == 0),  # First photo is main photo
            uploaded_at=datetime.now() - timedelta(days=random.randint(0, 30)),
            pet_id=pet.id,
            user_id=demo_user_id  # Assign all photos to demo user
        )
        
        db.add(pet_photo)
    
    db.commit()
    print("✅ Created 20 pet photos")
    
    print(f"\n🎉 Database seeding completed!")
    print(f"📊 Summary:")
    print(f"   • Users: {len(users)}")
    print(f"   • Pets: {len(pets)}")
    print(f"   • Journal Entries: 50")
    print(f"   • Quick Logs: 100")
    print(f"   • Pet Photos: 20")

def main():
    """Main function to run the seed script"""
    db = SessionLocal()
    try:
        create_sample_data(db)
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
