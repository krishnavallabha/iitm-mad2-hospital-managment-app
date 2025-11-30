"""
Script to seed the database with dummy doctors
Run this after initializing the database with init_db.py
"""
from app import app
from database import db
from models import User, Doctor, Department
from werkzeug.security import generate_password_hash

def seed_doctors():
    """Add dummy doctors to the database"""
    with app.app_context():
        # Get all departments
        departments = Department.query.all()
        if not departments:
            print("[ERROR] No departments found! Please run init_db.py first to create departments.")
            return
        
        # Dummy doctors data
        doctors_data = [
            {
                'username': 'dr.smith',
                'email': 'john.smith@hospital.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'specialization': 'Cardiology',
                'phone': '+1-555-0101',
                'license_number': 'MD-CARD-001',
                'experience_years': 15,
                'consultation_fee': 150.00,
                'bio': 'Board-certified cardiologist with 15 years of experience in treating heart conditions. Specializes in preventive cardiology and interventional procedures.'
            },
            {
                'username': 'dr.johnson',
                'email': 'sarah.johnson@hospital.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'specialization': 'Neurology',
                'phone': '+1-555-0102',
                'license_number': 'MD-NEURO-002',
                'experience_years': 12,
                'consultation_fee': 200.00,
                'bio': 'Expert neurologist specializing in stroke treatment and neurological disorders. Published researcher with focus on neurodegenerative diseases.'
            },
            {
                'username': 'dr.williams',
                'email': 'michael.williams@hospital.com',
                'first_name': 'Michael',
                'last_name': 'Williams',
                'specialization': 'Orthopedics',
                'phone': '+1-555-0103',
                'license_number': 'MD-ORTHO-003',
                'experience_years': 20,
                'consultation_fee': 180.00,
                'bio': 'Orthopedic surgeon with expertise in joint replacement and sports medicine. Performed over 1000 successful surgeries.'
            },
            {
                'username': 'dr.brown',
                'email': 'emily.brown@hospital.com',
                'first_name': 'Emily',
                'last_name': 'Brown',
                'specialization': 'Pediatrics',
                'phone': '+1-555-0104',
                'license_number': 'MD-PED-004',
                'experience_years': 10,
                'consultation_fee': 120.00,
                'bio': 'Caring pediatrician dedicated to children\'s health and wellness. Specializes in developmental pediatrics and childhood vaccinations.'
            },
            {
                'username': 'dr.davis',
                'email': 'david.davis@hospital.com',
                'first_name': 'David',
                'last_name': 'Davis',
                'specialization': 'Dermatology',
                'phone': '+1-555-0105',
                'license_number': 'MD-DERM-005',
                'experience_years': 8,
                'consultation_fee': 140.00,
                'bio': 'Dermatologist specializing in skin cancer detection and cosmetic dermatology. Expert in treating acne, psoriasis, and eczema.'
            },
            {
                'username': 'dr.miller',
                'email': 'lisa.miller@hospital.com',
                'first_name': 'Lisa',
                'last_name': 'Miller',
                'specialization': 'General Medicine',
                'phone': '+1-555-0106',
                'license_number': 'MD-GEN-006',
                'experience_years': 18,
                'consultation_fee': 100.00,
                'bio': 'Experienced general practitioner providing comprehensive primary care. Focuses on preventive medicine and chronic disease management.'
            },
            {
                'username': 'dr.wilson',
                'email': 'robert.wilson@hospital.com',
                'first_name': 'Robert',
                'last_name': 'Wilson',
                'specialization': 'Psychiatry',
                'phone': '+1-555-0107',
                'license_number': 'MD-PSYCH-007',
                'experience_years': 14,
                'consultation_fee': 160.00,
                'bio': 'Board-certified psychiatrist specializing in mood disorders, anxiety, and depression. Provides both medication management and therapy.'
            },
            {
                'username': 'dr.moore',
                'email': 'jennifer.moore@hospital.com',
                'first_name': 'Jennifer',
                'last_name': 'Moore',
                'specialization': 'Oncology',
                'phone': '+1-555-0108',
                'license_number': 'MD-ONCO-008',
                'experience_years': 16,
                'consultation_fee': 250.00,
                'bio': 'Oncologist with expertise in breast cancer and hematologic malignancies. Committed to providing compassionate cancer care.'
            },
            {
                'username': 'dr.taylor',
                'email': 'james.taylor@hospital.com',
                'first_name': 'James',
                'last_name': 'Taylor',
                'specialization': 'Cardiology',
                'phone': '+1-555-0109',
                'license_number': 'MD-CARD-009',
                'experience_years': 11,
                'consultation_fee': 145.00,
                'bio': 'Cardiologist specializing in cardiac imaging and preventive cardiology. Expert in managing hypertension and heart failure.'
            },
            {
                'username': 'dr.anderson',
                'email': 'maria.anderson@hospital.com',
                'first_name': 'Maria',
                'last_name': 'Anderson',
                'specialization': 'Neurology',
                'phone': '+1-555-0110',
                'license_number': 'MD-NEURO-010',
                'experience_years': 9,
                'consultation_fee': 190.00,
                'bio': 'Neurologist with special interest in epilepsy and movement disorders. Provides comprehensive neurological care for all ages.'
            },
            {
                'username': 'dr.thomas',
                'email': 'patricia.thomas@hospital.com',
                'first_name': 'Patricia',
                'last_name': 'Thomas',
                'specialization': 'Pediatrics',
                'phone': '+1-555-0111',
                'license_number': 'MD-PED-011',
                'experience_years': 13,
                'consultation_fee': 125.00,
                'bio': 'Pediatrician with expertise in adolescent medicine and pediatric emergency care. Passionate about child health advocacy.'
            },
            {
                'username': 'dr.jackson',
                'email': 'william.jackson@hospital.com',
                'first_name': 'William',
                'last_name': 'Jackson',
                'specialization': 'Orthopedics',
                'phone': '+1-555-0112',
                'license_number': 'MD-ORTHO-012',
                'experience_years': 17,
                'consultation_fee': 175.00,
                'bio': 'Orthopedic surgeon specializing in spine surgery and minimally invasive procedures. Expert in treating back and neck pain.'
            },
            {
                'username': 'dr.white',
                'email': 'elizabeth.white@hospital.com',
                'first_name': 'Elizabeth',
                'last_name': 'White',
                'specialization': 'Dermatology',
                'phone': '+1-555-0113',
                'license_number': 'MD-DERM-013',
                'experience_years': 7,
                'consultation_fee': 135.00,
                'bio': 'Dermatologist with expertise in medical and surgical dermatology. Specializes in skin cancer surgery and Mohs micrographic surgery.'
            },
            {
                'username': 'dr.harris',
                'email': 'christopher.harris@hospital.com',
                'first_name': 'Christopher',
                'last_name': 'Harris',
                'specialization': 'General Medicine',
                'phone': '+1-555-0114',
                'license_number': 'MD-GEN-014',
                'experience_years': 19,
                'consultation_fee': 110.00,
                'bio': 'Family medicine physician providing comprehensive care for all ages. Focuses on building long-term patient relationships.'
            },
            {
                'username': 'dr.martin',
                'email': 'nancy.martin@hospital.com',
                'first_name': 'Nancy',
                'last_name': 'Martin',
                'specialization': 'Psychiatry',
                'phone': '+1-555-0115',
                'license_number': 'MD-PSYCH-015',
                'experience_years': 15,
                'consultation_fee': 165.00,
                'bio': 'Psychiatrist specializing in child and adolescent psychiatry. Provides family-centered mental health care.'
            }
        ]
        
        print("="*60)
        print("Seeding Dummy Doctors")
        print("="*60)
        
        created_count = 0
        skipped_count = 0
        
        for doctor_data in doctors_data:
            # Check if doctor already exists
            existing_user = User.query.filter_by(username=doctor_data['username']).first()
            if existing_user:
                print(f"[SKIP] Skipping {doctor_data['first_name']} {doctor_data['last_name']} - already exists")
                skipped_count += 1
                continue
            
            # Find department by name
            department = next((d for d in departments if d.name == doctor_data['specialization']), None)
            if not department:
                print(f"[ERROR] Department '{doctor_data['specialization']}' not found! Skipping {doctor_data['first_name']} {doctor_data['last_name']}")
                skipped_count += 1
                continue
            
            try:
                # Create user account
                user = User(
                    username=doctor_data['username'],
                    email=doctor_data['email'],
                    role='doctor'
                )
                user.set_password('doctor123')  # Default password for all dummy doctors
                db.session.add(user)
                db.session.flush()  # Get user.id
                
                # Create doctor profile
                doctor = Doctor(
                    user_id=user.id,
                    first_name=doctor_data['first_name'],
                    last_name=doctor_data['last_name'],
                    specialization_id=department.id,
                    phone=doctor_data['phone'],
                    license_number=doctor_data['license_number'],
                    experience_years=doctor_data['experience_years'],
                    consultation_fee=doctor_data['consultation_fee'],
                    bio=doctor_data['bio'],
                    is_active=True
                )
                db.session.add(doctor)
                db.session.commit()
                
                created_count += 1
                print(f"[OK] Created: Dr. {doctor_data['first_name']} {doctor_data['last_name']} - {doctor_data['specialization']}")
                
            except Exception as e:
                db.session.rollback()
                print(f"[ERROR] Error creating {doctor_data['first_name']} {doctor_data['last_name']}: {str(e)}")
                skipped_count += 1
        
        print("="*60)
        print(f"[SUCCESS] Successfully created {created_count} doctors")
        if skipped_count > 0:
            print(f"[INFO] Skipped {skipped_count} doctors (already exist or errors)")
        print("="*60)
        print("\nDefault password for all dummy doctors: doctor123")
        print("[IMPORTANT] Change passwords after first login!")
        print("="*60)

if __name__ == '__main__':
    seed_doctors()

