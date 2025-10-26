#!/usr/bin/env python3
"""
Initialize the AgentAid database with proper schema
"""

import sqlite3
import os
from pathlib import Path

def init_database():
    """Initialize the database with proper schema"""
    
    # Get the database path
    db_dir = Path(__file__).parent
    db_path = db_dir / "agent_aid.db"
    
    # Remove existing database if it exists
    if db_path.exists():
        print(f"🗑️  Removing existing database: {db_path}")
        db_path.unlink()
    
    # Create database directory
    db_dir.mkdir(exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    print(f"📊 Creating database: {db_path}")
    
    # Read and execute the schema
    schema_file = db_dir / "inventory.sql"
    if schema_file.exists():
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema
        conn.executescript(schema_sql)
        print("✅ Database schema created")
    else:
        print("❌ Schema file not found")
        return False
    
    # Add category column if it doesn't exist
    try:
        conn.execute("ALTER TABLE items ADD COLUMN category TEXT DEFAULT 'general'")
        print("✅ Added category column")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.close()
    print("✅ Database initialization complete")
    return True

if __name__ == "__main__":
    init_database()
