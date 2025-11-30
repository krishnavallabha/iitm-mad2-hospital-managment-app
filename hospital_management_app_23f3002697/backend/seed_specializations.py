from app import app
from database import db
from models import Department

def seed_specializations():
    specializations = {
        "Organ / System Specialists": [
            "Nephrologist", "Urologist", "Cardiologist", "Cardiothoracic Surgeon",
            "Neurologist", "Neurosurgeon", "Orthopedic Surgeon / Orthopedist",
            "Rheumatologist", "Pulmonologist", "Thoracic Surgeon", "Gastroenterologist",
            "Hepatologist", "Dermatologist", "Ophthalmologist", "Optometrist",
            "ENT Specialist (Otolaryngologist)", "Dentist", "Oral Surgeon",
            "Periodontist", "Orthodontist", "Endocrinologist", "Hematologist",
            "Oncologist", "Gynecologist", "Obstetrician", "Andrologist",
            "Immunologist", "Palliative Care Specialist"
        ],
        "Age-Based": [
            "Pediatrician", "Neonatologist", "Geriatrician"
        ],
        "Surgical": [
            "General Surgeon", "Plastic Surgeon", "Orthopedic Surgeon",
            "Cardiothoracic Surgeon", "Neurosurgeon", "Vascular Surgeon",
            "Colorectal Surgeon", "Trauma Surgeon"
        ],
        "Cancer": [
            "Medical Oncologist", "Surgical Oncologist", "Radiation Oncologist"
        ],
        "Diagnostic / Lab": [
            "Radiologist", "Pathologist"
        ],
        "Mental Health": [
            "Psychiatrist", "Psychologist"
        ]
    }

    with app.app_context():
        print("Seeding specializations...")
        
        for category, specs in specializations.items():
            for spec_name in specs:
                # Check if department exists
                dept = Department.query.filter_by(name=spec_name).first()
                if dept:
                    # Update category if it exists
                    dept.category = category
                    print(f"  [UPDATED] {spec_name} -> {category}")
                else:
                    # Create new department
                    new_dept = Department(name=spec_name, category=category)
                    db.session.add(new_dept)
                    print(f"  [CREATED] {spec_name} -> {category}")
        
        db.session.commit()
        print("[OK] Specializations seeded successfully!")

if __name__ == '__main__':
    seed_specializations()
