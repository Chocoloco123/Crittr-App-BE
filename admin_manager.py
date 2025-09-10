#!/usr/bin/env python3
"""
Admin User Management Script
Easy-to-use script for managing admin users
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection"""
    database_url = os.getenv("DATABASE_URL", "postgresql://crittr_user:crittr_password@localhost:5432/crittr")
    return create_engine(database_url)

def list_admins():
    """List all admin users"""
    engine = get_db_connection()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT email, name, is_active, last_login, login_count, created_at 
            FROM admin_users 
            ORDER BY created_at;
        """))
        
        print("📋 Current Admin Users:")
        print("-" * 80)
        for row in result:
            status = "✅ Active" if row.is_active else "❌ Inactive"
            last_login = row.last_login.strftime("%Y-%m-%d %H:%M") if row.last_login else "Never"
            print(f"Email: {row.email}")
            print(f"Name: {row.name}")
            print(f"Status: {status}")
            print(f"Login Count: {row.login_count}")
            print(f"Last Login: {last_login}")
            print(f"Created: {row.created_at.strftime('%Y-%m-%d %H:%M')}")
            print("-" * 80)

def add_admin(email, name=None):
    """Add a new admin user"""
    if not name:
        name = email.split('@')[0].title()
    
    engine = get_db_connection()
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                INSERT INTO admin_users (email, name, is_active) 
                VALUES (:email, :name, true) 
                ON CONFLICT (email) DO UPDATE SET 
                    name = EXCLUDED.name,
                    is_active = true,
                    updated_at = NOW();
            """), {"email": email, "name": name})
            conn.commit()
            print(f"✅ Admin user {email} added/updated successfully!")
        except Exception as e:
            print(f"❌ Error adding admin user: {e}")

def remove_admin(email):
    """Remove admin privileges (set inactive)"""
    engine = get_db_connection()
    with engine.connect() as conn:
        try:
            result = conn.execute(text("""
                UPDATE admin_users 
                SET is_active = false, updated_at = NOW() 
                WHERE email = :email;
            """), {"email": email})
            conn.commit()
            
            if result.rowcount > 0:
                print(f"✅ Admin privileges removed for {email}")
            else:
                print(f"❌ Admin user {email} not found")
        except Exception as e:
            print(f"❌ Error removing admin: {e}")

def activate_admin(email):
    """Reactivate admin privileges"""
    engine = get_db_connection()
    with engine.connect() as conn:
        try:
            result = conn.execute(text("""
                UPDATE admin_users 
                SET is_active = true, updated_at = NOW() 
                WHERE email = :email;
            """), {"email": email})
            conn.commit()
            
            if result.rowcount > 0:
                print(f"✅ Admin privileges reactivated for {email}")
            else:
                print(f"❌ Admin user {email} not found")
        except Exception as e:
            print(f"❌ Error reactivating admin: {e}")

def main():
    """Main function with interactive menu"""
    if len(sys.argv) < 2:
        print("🔧 Admin User Management Tool")
        print("\nUsage:")
        print("  python admin_manager.py list                    # List all admins")
        print("  python admin_manager.py add <email> [name]      # Add admin")
        print("  python admin_manager.py remove <email>           # Remove admin")
        print("  python admin_manager.py activate <email>        # Reactivate admin")
        print("\nExamples:")
        print("  python admin_manager.py list")
        print("  python admin_manager.py add admin@example.com 'Admin User'")
        print("  python admin_manager.py remove admin@example.com")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_admins()
    elif command == "add":
        if len(sys.argv) < 3:
            print("❌ Please provide an email address")
            return
        email = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else None
        add_admin(email, name)
    elif command == "remove":
        if len(sys.argv) < 3:
            print("❌ Please provide an email address")
            return
        email = sys.argv[2]
        remove_admin(email)
    elif command == "activate":
        if len(sys.argv) < 3:
            print("❌ Please provide an email address")
            return
        email = sys.argv[2]
        activate_admin(email)
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
