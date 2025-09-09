#!/usr/bin/env python3
"""
Database migration script to rename gender column to sex in pets table
This script safely renames the column without affecting existing data
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Rename gender column to sex in pets table"""
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/crittr")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        print("🔄 Starting migration: Renaming gender column to sex in pets table...")
        
        with engine.connect() as conn:
            # Check if gender column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pets' AND column_name = 'gender'
            """))
            
            if not result.fetchone():
                print("❌ Gender column does not exist, skipping migration")
                return
            
            # Check if sex column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pets' AND column_name = 'sex'
            """))
            
            if result.fetchone():
                print("✅ Sex column already exists, skipping migration")
                return
            
            # Rename the column from gender to sex
            conn.execute(text("""
                ALTER TABLE pets 
                RENAME COLUMN gender TO sex
            """))
            
            # Update the comment on the column
            conn.execute(text("""
                COMMENT ON COLUMN pets.sex IS 'Pet sex: male, female, or unknown'
            """))
            
            conn.commit()
            
        print("✅ Successfully renamed gender column to sex in pets table")
        print("📝 Column details:")
        print("   • Old name: gender")
        print("   • New name: sex")
        print("   • Type: VARCHAR(20)")
        print("   • Nullable: Yes")
        print("   • Comment: Pet sex: male, female, or unknown")
        
        # Verify the data is still there
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT name, sex, species, breed 
                FROM pets 
                WHERE sex IS NOT NULL 
                ORDER BY name
            """))
            
            pets_with_sex = result.fetchall()
            print(f"\n✅ Verified {len(pets_with_sex)} pets with sex data:")
            for pet in pets_with_sex:
                print(f"   • {pet[0]} ({pet[2]}): {pet[1]}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
