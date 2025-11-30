from app import app
from database import db
from sqlalchemy import text

def update_schema():
    with app.app_context():
        print("Updating database schema...")
        
        # Add visit_type to appointments
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE appointments ADD COLUMN visit_type VARCHAR(20) DEFAULT 'In-person'"))
                conn.commit()
            print("[OK] Added visit_type to appointments")
        except Exception as e:
            print(f"[INFO] Could not add visit_type to appointments (might already exist): {e}")

        # Add tests_done to treatments
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE treatments ADD COLUMN tests_done TEXT"))
                conn.commit()
            print("[OK] Added tests_done to treatments")
        except Exception as e:
            print(f"[INFO] Could not add tests_done to treatments (might already exist): {e}")

        # Add medicines to treatments
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE treatments ADD COLUMN medicines TEXT"))
                conn.commit()
            print("[OK] Added medicines to treatments")
        except Exception as e:
            print(f"[INFO] Could not add medicines to treatments (might already exist): {e}")

        # Add attachments to treatments
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE treatments ADD COLUMN attachments TEXT"))
                conn.commit()
            print("[OK] Added attachments to treatments")
        except Exception as e:
            print(f"[INFO] Could not add attachments to treatments (might already exist): {e}")

        # Add positives to doctors
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE doctors ADD COLUMN positives TEXT"))
                conn.commit()
            print("[OK] Added positives to doctors")
        except Exception as e:
            print(f"[INFO] Could not add positives to doctors (might already exist): {e}")
            
        print("Schema update complete.")

if __name__ == '__main__':
    update_schema()
