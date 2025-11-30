from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from database import db

class User(db.Model):
    """Base User model for Admin, Doctor, and Patient"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'doctor', 'patient'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    doctor_profile = relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    patient_profile = relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class Department(db.Model):
    """Department/Specialization model"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100))  # New field for grouping
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    doctors = relationship('Doctor', backref='department', lazy='dynamic')
    
    def to_dict(self):
        """Convert department to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'doctors_count': self.doctors.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Doctor(db.Model):
    """Doctor model with specialization and availability"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    specialization_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    phone = db.Column(db.String(20))
    license_number = db.Column(db.String(50), unique=True)
    experience_years = db.Column(db.Integer, default=0)
    consultation_fee = db.Column(db.Numeric(10, 2), default=0.00)
    bio = db.Column(db.Text)
    positives = db.Column(db.Text)  # Highlights/achievements/positive points about the doctor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    appointments = relationship('Appointment', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')
    availability_slots = relationship('DoctorAvailability', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert doctor to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'specialization_id': self.specialization_id,
            'specialization': self.department.name if self.department else None,
            'phone': self.phone,
            'license_number': self.license_number,
            'experience_years': self.experience_years,
            'consultation_fee': float(self.consultation_fee) if self.consultation_fee else 0.00,
            'bio': self.bio,
            'positives': self.positives,
            'is_active': self.is_active,
            'email': self.user.email if self.user else None,
            'username': self.user.username if self.user else None
        }
    
    def __repr__(self):
        return f'<Doctor {self.first_name} {self.last_name}>'

class DoctorAvailability(db.Model):
    """Doctor availability slots for the next 7 days"""
    __tablename__ = 'doctor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Index for faster queries
    __table_args__ = (db.Index('idx_doctor_date', 'doctor_id', 'date'),)
    
    def to_dict(self):
        """Convert availability to dictionary"""
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'is_available': self.is_available
        }
    
    def __repr__(self):
        return f'<DoctorAvailability Doctor:{self.doctor_id} Date:{self.date}>'

class Patient(db.Model):
    """Patient model with profile and contact information"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))  # 'Male', 'Female', 'Other'
    address = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    blood_group = db.Column(db.String(5))
    medical_history = db.Column(db.Text)  # JSON or text field for medical history
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    appointments = relationship('Appointment', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert patient to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address': self.address,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'blood_group': self.blood_group,
            'medical_history': self.medical_history,
            'is_active': self.is_active,
            'email': self.user.email if self.user else None,
            'username': self.user.username if self.user else None
        }
    
    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'

class Appointment(db.Model):
    """Appointment model connecting patients and doctors"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    visit_type = db.Column(db.String(20), default='In-person')  # 'In-person', 'Online'
    status = db.Column(db.String(20), default='Booked')  # 'Booked', 'Completed', 'Cancelled'
    reason = db.Column(db.Text)  # Reason for visit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    treatment = relationship('Treatment', backref='appointment', uselist=False, cascade='all, delete-orphan')
    
    # Index for faster queries
    __table_args__ = (
        db.Index('idx_doctor_datetime', 'doctor_id', 'appointment_date', 'appointment_time'),
        db.Index('idx_patient_date', 'patient_id', 'appointment_date'),
        db.Index('idx_status', 'status'),
    )
    
    def to_dict(self):
        """Convert appointment to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'patient_name': f"{self.patient.first_name} {self.patient.last_name}" if self.patient else None,
            'doctor_name': f"{self.doctor.first_name} {self.doctor.last_name}" if self.doctor else None,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'visit_type': self.visit_type,
            'status': self.status,
            'reason': self.reason,
            'has_treatment': self.treatment is not None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Appointment {self.id} - Patient:{self.patient_id} Doctor:{self.doctor_id} Date:{self.appointment_date}>'

class Treatment(db.Model):
    """Treatment record for appointments"""
    __tablename__ = 'treatments'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), unique=True, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    tests_done = db.Column(db.Text)  # JSON or text
    prescription = db.Column(db.Text)
    medicines = db.Column(db.Text)  # JSON or text
    attachments = db.Column(db.Text)  # JSON list of file paths/urls
    notes = db.Column(db.Text)  # Doctor's notes
    follow_up_date = db.Column(db.Date)  # Next visit suggested by doctor
    follow_up_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert treatment to dictionary"""
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'diagnosis': self.diagnosis,
            'tests_done': self.tests_done,
            'prescription': self.prescription,
            'medicines': self.medicines,
            'attachments': self.attachments,
            'notes': self.notes,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'follow_up_notes': self.follow_up_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'appointment': self.appointment.to_dict() if self.appointment else None
        }
    
    def __repr__(self):
        return f'<Treatment Appointment:{self.appointment_id}>'

