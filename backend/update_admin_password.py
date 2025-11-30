"""
Script to update the admin user's password
"""
from app import app
from database import db
from models import User

def update_admin_password():
    """Update the admin user's password to krishna2622"""
    with app.app_context():
        admin = User.query.filter_by(role='admin', username='admin').first()
        
        if not admin:
            print("[ERROR] Admin user not found!")
            return
        
        print(f"Found admin user: {admin.username} ({admin.email})")
        admin.set_password('krishna2622')
        db.session.commit()
        print("[OK] Admin password updated successfully!")
        print("New password: krishna2622")

if __name__ == '__main__':
    update_admin_password()

