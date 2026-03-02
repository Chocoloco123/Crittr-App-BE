#!/usr/bin/env python3
"""
Migration script to add photo_albums and photos tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the migration to add photo album tables"""
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/crittr")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            try:
                # Create photo_albums table
                create_albums_table_sql = """
                CREATE TABLE IF NOT EXISTS photo_albums (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    cover_photo_id INTEGER,
                    pet_id INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
                    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    is_public BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                
                connection.execute(text(create_albums_table_sql))
                
                # Create photos table
                create_photos_table_sql = """
                CREATE TABLE IF NOT EXISTS photos (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR NOT NULL,
                    original_filename VARCHAR NOT NULL,
                    file_path VARCHAR NOT NULL,
                    mime_type VARCHAR NOT NULL,
                    file_size INTEGER NOT NULL,
                    width INTEGER,
                    height INTEGER,
                    album_id INTEGER NOT NULL REFERENCES photo_albums(id) ON DELETE CASCADE,
                    pet_id INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
                    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    caption TEXT,
                    tags TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                
                connection.execute(text(create_photos_table_sql))
                
                # Add foreign key constraint for cover_photo_id
                add_cover_photo_fk_sql = """
                ALTER TABLE photo_albums 
                ADD CONSTRAINT fk_cover_photo 
                FOREIGN KEY (cover_photo_id) REFERENCES photos(id) ON DELETE SET NULL;
                """
                
                try:
                    connection.execute(text(add_cover_photo_fk_sql))
                except Exception as e:
                    # Constraint might already exist
                    print(f"Note: Cover photo foreign key constraint may already exist: {e}")
                
                # Create indexes for better performance
                indexes_sql = [
                    "CREATE INDEX IF NOT EXISTS idx_photo_albums_user_id ON photo_albums(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_photo_albums_pet_id ON photo_albums(pet_id);",
                    "CREATE INDEX IF NOT EXISTS idx_photo_albums_created_at ON photo_albums(created_at);",
                    "CREATE INDEX IF NOT EXISTS idx_photos_album_id ON photos(album_id);",
                    "CREATE INDEX IF NOT EXISTS idx_photos_user_id ON photos(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_photos_pet_id ON photos(pet_id);",
                    "CREATE INDEX IF NOT EXISTS idx_photos_created_at ON photos(created_at);",
                    "CREATE INDEX IF NOT EXISTS idx_photos_tags ON photos USING GIN(tags);"
                ]
                
                for index_sql in indexes_sql:
                    connection.execute(text(index_sql))
                
                # Commit transaction
                trans.commit()
                print("✅ Photo album migration completed successfully!")
                print("   - Created photo_albums table")
                print("   - Created photos table")
                print("   - Added foreign key constraints")
                print("   - Added indexes for performance")
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Migration failed: {str(e)}")
                raise
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔄 Running photo album migration...")
    run_migration()
