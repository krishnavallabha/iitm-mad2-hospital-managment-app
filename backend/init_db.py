"""
Database initialization script
Creates all tables and creates the default admin user
"""
from app import app
from database import db
from models import User, Doctor, Patient, Department, Appointment, Treatment, DoctorAvailability

def init_database():
    """Initialize database with tables and default admin user"""
    with app.app_context():
        # Drop all tables (for fresh start - comment out in production)
        # db.drop_all()
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("[OK] Database tables created successfully!")
        
        # Check if admin already exists
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print("[OK] Admin user already exists!")
            return
        
        # Create default admin user
        print("Creating default admin user...")
        admin_user = User(
            username='admin',
            email='admin@hospital.com',
            role='admin'
        )
        admin_user.set_password('krishna2622')  # Default password
        db.session.add(admin_user)
        
        # Create some default departments
        print("Creating default departments...")
        departments_data = [
            {'name': 'Cardiology', 'description': 'Heart and cardiovascular system'},
            {'name': 'Neurology', 'description': 'Brain and nervous system'},
            {'name': 'Orthopedics', 'description': 'Bones, joints, and muscles'},
            {'name': 'Pediatrics', 'description': 'Medical care for infants, children, and adolescents'},
            {'name': 'Dermatology', 'description': 'Skin, hair, and nails'},
            {'name': 'General Medicine', 'description': 'General health and wellness'},
            {'name': 'Psychiatry', 'description': 'Mental health and behavioral disorders'},
            {'name': 'Oncology', 'description': 'Cancer diagnosis and treatment'},
        ]
        
        for dept_data in departments_data:
            existing_dept = Department.query.filter_by(name=dept_data['name']).first()
            if not existing_dept:
                department = Department(**dept_data)
                db.session.add(department)
                print(f"  [OK] Created department: {dept_data['name']}")
        
        # Commit all changes
        db.session.commit()
        print("[OK] Database initialized successfully!")
        print("\n" + "="*50)
        print("Default Admin Credentials:")
        print("  Username: admin")
        print("  Email: admin@hospital.com")
        print("  Password: krishna2622")
        print("="*50)
        print("\n[IMPORTANT] Change the admin password after first login!")

if __name__ == '__main__':
    init_database()

