#!/usr/bin/env python3
"""
Migration script to create admin_users table and add initial admin users
Run this script to set up the admin system
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Create admin_users table and add initial admin users"""
    
    # Database connection
    database_url = os.getenv("DATABASE_URL", "postgresql://crittr_user:crittr_password@localhost:5432/crittr")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Create admin_users table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """))
            
            # Add initial admin users
            admin_users = [
                ('csarkki.swe@gmail.com', 'Caroline Sarkki'),
                # Add more admin users here as needed
            ]
            
            for email, name in admin_users:
                conn.execute(text("""
                    INSERT INTO admin_users (email, name) 
                    VALUES (:email, :name) 
                    ON CONFLICT (email) DO NOTHING;
                """), {"email": email, "name": name})
            
            conn.commit()
            print("✅ Admin users table created and initial admins added successfully!")
            
            # Show current admin users
            result = conn.execute(text("SELECT email, name, created_at FROM admin_users ORDER BY created_at;"))
            print("\n📋 Current admin users:")
            for row in result:
                print(f"  - {row.email} ({row.name}) - Added: {row.created_at}")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Running admin users migration...")
    run_migration()
    print("✅ Migration completed!")
