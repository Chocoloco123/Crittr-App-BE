#!/usr/bin/env python3
"""
Database migration script to add gender column to pets table
This script safely adds the gender column without affecting existing data
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Add gender column to pets table"""
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/crittr")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        print("🔄 Starting migration: Adding gender column to pets table...")
        
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pets' AND column_name = 'gender'
            """))
            
            if result.fetchone():
                print("✅ Gender column already exists, skipping migration")
                return
            
            # Add the gender column
            conn.execute(text("""
                ALTER TABLE pets 
                ADD COLUMN gender VARCHAR(20) NULL
            """))
            
            # Add a comment to the column
            conn.execute(text("""
                COMMENT ON COLUMN pets.gender IS 'Pet gender: male, female, or unknown'
            """))
            
            conn.commit()
            
        print("✅ Successfully added gender column to pets table")
        print("📝 Column details:")
        print("   • Name: gender")
        print("   • Type: VARCHAR(20)")
        print("   • Nullable: Yes")
        print("   • Default: NULL")
        print("   • Comment: Pet gender: male, female, or unknown")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
