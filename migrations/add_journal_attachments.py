#!/usr/bin/env python3
"""
Migration script to add journal_attachments table and update journal_entries table
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the migration to add journal_attachments table"""
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/crittr")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            try:
                # Create journal_attachments table
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS journal_attachments (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR NOT NULL,
                    original_filename VARCHAR NOT NULL,
                    file_path VARCHAR NOT NULL,
                    file_type VARCHAR NOT NULL,
                    mime_type VARCHAR NOT NULL,
                    file_size INTEGER NOT NULL,
                    journal_entry_id INTEGER NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
                    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                
                connection.execute(text(create_table_sql))
                
                # Create indexes for better performance
                indexes_sql = [
                    "CREATE INDEX IF NOT EXISTS idx_journal_attachments_journal_entry_id ON journal_attachments(journal_entry_id);",
                    "CREATE INDEX IF NOT EXISTS idx_journal_attachments_user_id ON journal_attachments(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_journal_attachments_file_type ON journal_attachments(file_type);"
                ]
                
                for index_sql in indexes_sql:
                    connection.execute(text(index_sql))
                
                # Commit transaction
                trans.commit()
                print("✅ Migration completed successfully!")
                print("   - Created journal_attachments table")
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
    print("🔄 Running journal attachments migration...")
    run_migration()
