"""
Admin routes for managing doctors, patients, and appointments
"""
from flask import Blueprint, request, jsonify
from auth import admin_required
from database import db
from models import User, Doctor, Patient, Department, Appointment, Treatment
from sqlalchemy import or_, func, and_
from datetime import datetime, date
from utils.cache import (
    invalidate_doctor_search_cache,
    invalidate_doctor_availability_cache,
)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard(current_user):
    """
    Admin dashboard with statistics
    """
    try:
        # Get statistics
        total_doctors = Doctor.query.filter_by(is_active=True).count()
        total_patients = Patient.query.filter_by(is_active=True).count()
        total_appointments = Appointment.query.count()
        total_departments = Department.query.count()
        
        today = date.today()
        upcoming_appointments = Appointment.query.filter(
            Appointment.appointment_date >= today,
            Appointment.status == 'Booked'
        ).count()
        
        completed_appointments = Appointment.query.filter_by(status='Completed').count()
        cancelled_appointments = Appointment.query.filter_by(status='Cancelled').count()
        
        # Recent appointments
        recent_appointments = Appointment.query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        ).limit(10).all()
        
        # Today's appointments
        today_appointments = Appointment.query.filter(
            Appointment.appointment_date == today
        ).order_by(Appointment.appointment_time).all()
        
        return jsonify({
            'role': 'admin',
            'statistics': {
                'total_doctors': total_doctors,
                'total_patients': total_patients,
                'total_departments': total_departments,
                'total_appointments': total_appointments,
                'upcoming_appointments': upcoming_appointments,
                'completed_appointments': completed_appointments,
                'cancelled_appointments': cancelled_appointments,
                'today_appointments': len(today_appointments)
            },
            'recent_appointments': [apt.to_dict() for apt in recent_appointments],
            'today_appointments': [apt.to_dict() for apt in today_appointments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to load dashboard: {str(e)}'}), 500

# ==================== DOCTOR MANAGEMENT ====================

@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_all_doctors(current_user):
    """
    Get all doctors with optional search/filter
    Query params: search, specialization_id, is_active
    """
    try:
        search = request.args.get('search', '').strip()
        specialization_id = request.args.get('specialization_id', type=int)
        is_active = request.args.get('is_active', type=str)
        
        query = Doctor.query
        
        # Filter by specialization
        if specialization_id:
            query = query.filter_by(specialization_id=specialization_id)
        
        # Filter by active status
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query = query.filter_by(is_active=is_active_bool)
        
        # Search by name
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    Doctor.first_name.ilike(search_pattern),
                    Doctor.last_name.ilike(search_pattern),
                    Doctor.license_number.ilike(search_pattern)
                )
            )
        
        doctors = query.all()
        
        return jsonify({
            'doctors': [doctor.to_dict() for doctor in doctors],
            'count': len(doctors)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get doctors: {str(e)}'}), 500

@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def add_doctor(current_user):
    """
    Add a new doctor
    Requires: username, email, password, first_name, last_name, specialization_id
    Optional: phone, license_number, experience_years, consultation_fee, bio
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'specialization_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        username = data.get('username').strip()
        email = data.get('email').strip().lower()
        password = data.get('password')
        first_name = data.get('first_name').strip()
        last_name = data.get('last_name').strip()
        specialization_id = data.get('specialization_id')
        
        # Check if specialization exists
        department = Department.query.get(specialization_id)
        if not department:
            return jsonify({'error': 'Invalid specialization/department'}), 400
        
        # Check if username/email already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Check license number uniqueness if provided
        license_number = data.get('license_number', '').strip()
        if license_number and Doctor.query.filter_by(license_number=license_number).first():
            return jsonify({'error': 'License number already exists'}), 400
        
        # Create user
        user = User(
            username=username,
            email=email,
            role='doctor'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            specialization_id=specialization_id,
            phone=data.get('phone', '').strip() if data.get('phone') else None,
            license_number=license_number or None,
            experience_years=data.get('experience_years', 0),
            consultation_fee=data.get('consultation_fee', 0.00),
            bio=data.get('bio', '').strip() if data.get('bio') else None,
            positives=data.get('positives', '').strip() if data.get('positives') else None,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(doctor)
        db.session.commit()
        invalidate_doctor_search_cache()
        
        return jsonify({
            'message': 'Doctor added successfully',
            'doctor': doctor.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add doctor: {str(e)}'}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@admin_required
def get_doctor(current_user, doctor_id):
    """Get doctor details by ID"""
    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        return jsonify({'doctor': doctor.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get doctor: {str(e)}'}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@admin_required
def update_doctor(current_user, doctor_id):
    """
    Update doctor profile
    """
    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        data = request.get_json()
        
        # Update doctor fields
        if 'first_name' in data:
            doctor.first_name = data['first_name'].strip()
        if 'last_name' in data:
            doctor.last_name = data['last_name'].strip()
        if 'specialization_id' in data:
            dept = Department.query.get(data['specialization_id'])
            if not dept:
                return jsonify({'error': 'Invalid specialization'}), 400
            doctor.specialization_id = data['specialization_id']
        if 'phone' in data:
            doctor.phone = data['phone'].strip() if data['phone'] else None
        if 'license_number' in data:
            license_num = data['license_number'].strip() if data['license_number'] else ''
            if license_num and Doctor.query.filter(
                Doctor.license_number == license_num,
                Doctor.id != doctor_id
            ).first():
                return jsonify({'error': 'License number already exists'}), 400
            doctor.license_number = license_num or None
        if 'experience_years' in data:
            doctor.experience_years = data['experience_years']
        if 'consultation_fee' in data:
            doctor.consultation_fee = data['consultation_fee']
        if 'bio' in data:
            doctor.bio = data['bio'].strip() if data['bio'] else None
        if 'positives' in data:
            doctor.positives = data['positives'].strip() if data['positives'] else None
        if 'is_active' in data:
            doctor.is_active = bool(data['is_active'])
        
        # Update user email if provided
        if 'email' in data and doctor.user:
            email = data['email'].strip().lower()
            if User.query.filter(User.email == email, User.id != doctor.user_id).first():
                return jsonify({'error': 'Email already registered'}), 400
            doctor.user.email = email
        
        doctor.updated_at = datetime.utcnow()
        db.session.commit()
        invalidate_doctor_search_cache()
        
        return jsonify({
            'message': 'Doctor updated successfully',
            'doctor': doctor.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update doctor: {str(e)}'}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@admin_required
def delete_doctor(current_user, doctor_id):
    """
    Permanently delete doctor and associated user account
    """
    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        
        # Get user before deletion for cache invalidation
        user = doctor.user
        doctor_id_for_cache = doctor.id
        
        # Delete doctor (this will cascade delete related appointments and availability slots)
        db.session.delete(doctor)
        
        # Delete associated user account if exists (must be after doctor deletion)
        if user:
            db.session.delete(user)
        
        db.session.commit()
        invalidate_doctor_search_cache()
        invalidate_doctor_availability_cache(doctor_id_for_cache)
        
        return jsonify({'message': 'Doctor deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to blacklist doctor: {str(e)}'}), 500

# ==================== PATIENT MANAGEMENT ====================

@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_all_patients(current_user):
    """
    Get all patients with optional search/filter
    Query params: search, is_active
    """
    try:
        search = request.args.get('search', '').strip()
        is_active = request.args.get('is_active', type=str)
        
        query = Patient.query
        
        # Filter by active status
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query = query.filter_by(is_active=is_active_bool)
        
        # Search by name, ID, phone, email
        if search:
            search_pattern = f'%{search}%'
            query = query.join(User).filter(
                or_(
                    Patient.first_name.ilike(search_pattern),
                    Patient.last_name.ilike(search_pattern),
                    Patient.phone.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.username.ilike(search_pattern)
                )
            )
        
        patients = query.all()
        
        return jsonify({
            'patients': [patient.to_dict() for patient in patients],
            'count': len(patients)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get patients: {str(e)}'}), 500

@admin_bp.route('/patients/<int:patient_id>', methods=['GET'])
@admin_required
def get_patient(current_user, patient_id):
    """Get patient details by ID"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # Get patient's appointment history
        appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
            Appointment.appointment_date.desc()
        ).all()
        
        patient_dict = patient.to_dict()
        patient_dict['appointments'] = [apt.to_dict() for apt in appointments]
        
        return jsonify({'patient': patient_dict}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get patient: {str(e)}'}), 500

@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@admin_required
def update_patient(current_user, patient_id):
    """
    Update patient profile
    """
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        # Update patient fields
        if 'first_name' in data:
            patient.first_name = data['first_name'].strip()
        if 'last_name' in data:
            patient.last_name = data['last_name'].strip()
        if 'phone' in data:
            patient.phone = data['phone'].strip() or None
        if 'date_of_birth' in data:
            patient.date_of_birth = data['date_of_birth']
        if 'gender' in data:
            patient.gender = data['gender'].strip() or None
        if 'address' in data:
            patient.address = data['address'].strip() or None
        if 'emergency_contact_name' in data:
            patient.emergency_contact_name = data['emergency_contact_name'].strip() or None
        if 'emergency_contact_phone' in data:
            patient.emergency_contact_phone = data['emergency_contact_phone'].strip() or None
        if 'blood_group' in data:
            patient.blood_group = data['blood_group'].strip() or None
        if 'medical_history' in data:
            patient.medical_history = data['medical_history']
        if 'is_active' in data:
            patient.is_active = bool(data['is_active'])
        
        # Update user email if provided
        if 'email' in data and patient.user:
            email = data['email'].strip().lower()
            if User.query.filter(User.email == email, User.id != patient.user_id).first():
                return jsonify({'error': 'Email already registered'}), 400
            patient.user.email = email
        
        patient.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Patient updated successfully',
            'patient': patient.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update patient: {str(e)}'}), 500

@admin_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
@admin_required
def delete_patient(current_user, patient_id):
    """
    Permanently delete patient and associated user account
    """
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # Get user before deletion
        user = patient.user
        
        # Delete patient (this will cascade delete related records if configured)
        db.session.delete(patient)
        
        # Delete associated user account if exists
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        return jsonify({'message': 'Patient deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete patient: {str(e)}'}), 500

# ==================== APPOINTMENT MANAGEMENT ====================

@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def get_all_appointments(current_user):
    """
    Get all appointments with optional filters
    Query params: status, date_from, date_to, doctor_id, patient_id
    """
    try:
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        doctor_id = request.args.get('doctor_id', type=int)
        patient_id = request.args.get('patient_id', type=int)
        
        query = Appointment.query
        
        if status:
            query = query.filter_by(status=status)
        
        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)
        
        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)
        
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        
        appointments = query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        ).all()
        
        return jsonify({
            'appointments': [apt.to_dict() for apt in appointments],
            'count': len(appointments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get appointments: {str(e)}'}), 500

@admin_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@admin_required
def get_appointment(current_user, appointment_id):
    """Get appointment details"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        apt_dict = appointment.to_dict()
        
        if appointment.treatment:
            apt_dict['treatment'] = appointment.treatment.to_dict()
        
        return jsonify({'appointment': apt_dict}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get appointment: {str(e)}'}), 500

@admin_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@admin_required
def update_appointment(current_user, appointment_id):
    """
    Update appointment (admin can modify date, time, status, etc.)
    """
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.get_json()
        
        # Check for conflicts if date/time is being changed
        if 'appointment_date' in data or 'appointment_time' in data:
            new_date = data.get('appointment_date', appointment.appointment_date)
            new_time = data.get('appointment_time', appointment.appointment_time)
            
            # Check if doctor has another appointment at same time
            conflict = Appointment.query.filter(
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.appointment_date == new_date,
                Appointment.appointment_time == new_time,
                Appointment.id != appointment_id,
                Appointment.status == 'Booked'
            ).first()
            
            if conflict:
                return jsonify({'error': 'Doctor already has an appointment at this time'}), 400
        
        # Update fields
        if 'appointment_date' in data:
            appointment.appointment_date = data['appointment_date']
        if 'appointment_time' in data:
            appointment.appointment_time = data['appointment_time']
        if 'status' in data:
            appointment.status = data['status']
        if 'reason' in data:
            appointment.reason = data['reason'].strip() or None
        
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment updated successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update appointment: {str(e)}'}), 500

@admin_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@admin_required
def cancel_appointment(current_user, appointment_id):
    """
    Cancel appointment (admin can cancel any appointment)
    """
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.status = 'Cancelled'
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Appointment cancelled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to cancel appointment: {str(e)}'}), 500

# ==================== DEPARTMENTS ====================

@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments(current_user):
    """Get all departments"""
    try:
        departments = Department.query.all()
        return jsonify({
            'departments': [dept.to_dict() for dept in departments]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get departments: {str(e)}'}), 500

@admin_bp.route('/departments', methods=['POST'])
@admin_required
def add_department(current_user):
    """Add a new department"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Department name is required'}), 400
        
        name = data['name'].strip()
        
        if Department.query.filter_by(name=name).first():
            return jsonify({'error': 'Department already exists'}), 400
        
        department = Department(
            name=name,
            description=data.get('description', '').strip() or None
        )
        
        db.session.add(department)
        db.session.commit()
        
        return jsonify({
            'message': 'Department added successfully',
            'department': department.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add department: {str(e)}'}), 500

@admin_bp.route('/departments/<int:department_id>', methods=['GET'])
@admin_required
def get_department_details(current_user, department_id):
    """Get department details with list of doctors"""
    try:
        department = Department.query.get_or_404(department_id)
        
        # Get doctors in this department
        doctors = Doctor.query.filter_by(
            specialization_id=department_id,
            is_active=True
        ).all()
        
        dept_dict = department.to_dict()
        dept_dict['doctors'] = [{
            'id': doc.id,
            'first_name': doc.first_name,
            'last_name': doc.last_name,
            'full_name': f"{doc.first_name} {doc.last_name}",
            'email': doc.user.email if doc.user else None,
            'phone': doc.phone,
            'experience_years': doc.experience_years,
            'bio': doc.bio,
            'positives': doc.positives,
            'license_number': doc.license_number,
            'is_active': doc.is_active
        } for doc in doctors]
        
        return jsonify({
            'department': dept_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get department details: {str(e)}'}), 500

@admin_bp.route('/departments/<int:department_id>', methods=['PUT'])
@admin_required
def update_department(current_user, department_id):
    """Update a department"""
    try:
        department = Department.query.get_or_404(department_id)
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Department name is required'}), 400
        
        name = data['name'].strip()
        
        # Check if name already exists (excluding current department)
        existing = Department.query.filter_by(name=name).first()
        if existing and existing.id != department_id:
            return jsonify({'error': 'Department name already exists'}), 400
        
        department.name = name
        department.description = data.get('description', '').strip() or None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Department updated successfully',
            'department': department.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update department: {str(e)}'}), 500

@admin_bp.route('/departments/<int:department_id>', methods=['DELETE'])
@admin_required
def delete_department(current_user, department_id):
    """Delete a department"""
    try:
        department = Department.query.get_or_404(department_id)
        
        # Check if department has doctors
        doctor_count = Doctor.query.filter_by(specialization_id=department_id).count()
        if doctor_count > 0:
            return jsonify({
                'error': f'Cannot delete department. {doctor_count} doctor(s) are assigned to this department. Please reassign them first.'
            }), 400
        
        db.session.delete(department)
        db.session.commit()
        
        return jsonify({
            'message': 'Department deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete department: {str(e)}'}), 500

# ==================== ANALYTICS ====================

@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics(current_user):
    """
    Get analytics data for Chart.js
    Returns appointment trends and specialization demand
    """
    try:
        from datetime import timedelta
        
        # Get date range (default: last 30 days)
        days = request.args.get('days', type=int, default=30)
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Appointment trends (daily for last 7 days, weekly for longer periods)
        if days <= 7:
            # Daily data
            daily_appointments = db.session.query(
                func.date(Appointment.appointment_date).label('date'),
                func.count(Appointment.id).label('count')
            ).filter(
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date
            ).group_by(
                func.date(Appointment.appointment_date)
            ).order_by(
                func.date(Appointment.appointment_date)
            ).all()
            
            appointment_trends = {
                'labels': [str(day[0]) for day in daily_appointments],
                'data': [day[1] for day in daily_appointments]
            }
        else:
            # Weekly data - use date formatting compatible with SQLite
            weekly_appointments = db.session.query(
                func.strftime('%Y-%W', Appointment.appointment_date).label('week'),
                func.count(Appointment.id).label('count')
            ).filter(
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date
            ).group_by(
                func.strftime('%Y-%W', Appointment.appointment_date)
            ).order_by(
                func.strftime('%Y-%W', Appointment.appointment_date)
            ).all()
            
            appointment_trends = {
                'labels': [week[0] for week in weekly_appointments],
                'data': [week[1] for week in weekly_appointments]
            }
        
        # Specialization demand (appointments by department)
        specialization_demand = db.session.query(
            Department.name.label('department'),
            func.count(Appointment.id).label('count')
        ).join(
            Doctor, Department.id == Doctor.specialization_id
        ).join(
            Appointment, Doctor.id == Appointment.doctor_id
        ).filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).group_by(
            Department.name
        ).order_by(
            func.count(Appointment.id).desc()
        ).all()
        
        specialization_data = {
            'labels': [dept[0] for dept in specialization_demand],
            'data': [dept[1] for dept in specialization_demand]
        }
        
        # Status distribution
        status_distribution = db.session.query(
            Appointment.status,
            func.count(Appointment.id).label('count')
        ).filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).group_by(
            Appointment.status
        ).all()
        
        status_data = {
            'labels': [status[0] for status in status_distribution],
            'data': [status[1] for status in status_distribution]
        }
        
        # Top performing doctors (by appointment count)
        top_doctors = db.session.query(
            Doctor.id,
            Doctor.first_name,
            Doctor.last_name,
            Doctor.specialization_id,
            Doctor.user_id,
            func.count(Appointment.id).label('appointment_count')
        ).outerjoin(
            Appointment, 
            and_(
                Doctor.id == Appointment.doctor_id,
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date
            )
        ).filter(
            Doctor.is_active == True
        ).group_by(
            Doctor.id,
            Doctor.first_name,
            Doctor.last_name,
            Doctor.specialization_id,
            Doctor.user_id
        ).having(
            func.count(Appointment.id) > 0
        ).order_by(
            func.count(Appointment.id).desc()
        ).limit(10).all()
        
        # Get department names and user emails for doctors
        top_doctors_data = []
        for doc in top_doctors:
            department = Department.query.get(doc.specialization_id)
            doctor_user = User.query.get(doc.user_id) if doc.user_id else None
            
            top_doctors_data.append({
                'id': doc.id,
                'first_name': doc.first_name,
                'last_name': doc.last_name,
                'full_name': f"{doc.first_name} {doc.last_name}",
                'email': doctor_user.email if doctor_user else None,
                'specialization': department.name if department else 'N/A',
                'appointment_count': doc.appointment_count or 0
            })
        
        return jsonify({
            'appointment_trends': appointment_trends,
            'specialization_demand': specialization_data,
            'status_distribution': status_data,
            'top_doctors': top_doctors_data,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get analytics: {str(e)}'}), 500

