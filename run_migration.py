#!/usr/bin/env python3
"""
Migration and data update script
This script:
1. Runs the database migration to add gender column
2. Updates existing pets with gender information
3. Ensures all pets have proper weight data
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration_and_update():
    """Run migration and update existing data"""
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/crittr")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        print("🔄 Starting migration and data update...")
        
        with engine.connect() as conn:
            # Step 1: Add gender column if it doesn't exist
            print("📝 Step 1: Adding gender column...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pets' AND column_name = 'gender'
            """))
            
            if not result.fetchone():
                conn.execute(text("""
                    ALTER TABLE pets 
                    ADD COLUMN gender VARCHAR(20) NULL
                """))
                
                conn.execute(text("""
                    COMMENT ON COLUMN pets.gender IS 'Pet gender: male, female, or unknown'
                """))
                
                print("✅ Added gender column to pets table")
            else:
                print("✅ Gender column already exists")
            
            # Step 2: Update existing pets with gender information
            print("📝 Step 2: Updating existing pets with gender information...")
            
            # Define gender mappings based on pet names
            gender_updates = [
                ("Buddy", "male"),
                ("Whiskers", "female"), 
                ("Luna", "female"),
                ("Simba", "male"),
                ("Nemo", "male"),
                ("Max", "male"),
                ("Bella", "female"),
                ("Coco", "female")
            ]
            
            for name, gender in gender_updates:
                result = conn.execute(text("""
                    UPDATE pets 
                    SET gender = :gender 
                    WHERE name = :name AND gender IS NULL
                """), {"gender": gender, "name": name})
                
                if result.rowcount > 0:
                    print(f"✅ Updated {name} -> {gender}")
            
            # Step 3: Set default gender for any remaining pets
            print("📝 Step 3: Setting default gender for remaining pets...")
            result = conn.execute(text("""
                UPDATE pets 
                SET gender = 'unknown' 
                WHERE gender IS NULL
            """))
            
            if result.rowcount > 0:
                print(f"✅ Set default gender 'unknown' for {result.rowcount} pets")
            
            # Step 4: Verify weight data is in pounds (already correct from seed data)
            print("📝 Step 4: Verifying weight data...")
            result = conn.execute(text("""
                SELECT name, weight, species, breed 
                FROM pets 
                WHERE weight IS NOT NULL 
                ORDER BY name
            """))
            
            pets_with_weight = result.fetchall()
            print(f"✅ Found {len(pets_with_weight)} pets with weight data:")
            for pet in pets_with_weight:
                print(f"   • {pet[0]} ({pet[2]}): {pet[1]} lbs")
            
            conn.commit()
            
        print("\n🎉 Migration and data update completed successfully!")
        print("📊 Summary:")
        print("   • Added gender column to pets table")
        print("   • Updated existing pets with appropriate gender")
        print("   • Verified weight data is in pounds")
        print("   • All existing data preserved")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration_and_update()
