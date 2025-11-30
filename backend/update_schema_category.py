from app import app
from database import db
from sqlalchemy import text

def update_schema_category():
    with app.app_context():
        print("Updating database schema for categories...")
        
        try:
            with db.engine.connect() as conn:
                # Check if column exists first (SQLite doesn't support IF NOT EXISTS for columns easily in all versions, but we can try adding it)
                # For simplicity in this context, we'll try to add it and catch the error if it exists
                conn.execute(text("ALTER TABLE departments ADD COLUMN category VARCHAR(100)"))
                conn.commit()
            print("[OK] Added category to departments")
        except Exception as e:
            print(f"[INFO] Could not add category to departments (might already exist): {e}")
            
        print("Schema update complete.")

if __name__ == '__main__':
    update_schema_category()
