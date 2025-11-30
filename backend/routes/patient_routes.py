"""
Patient routes for booking appointments, viewing doctors, and managing profile
"""
from flask import Blueprint, request, jsonify
from auth import patient_required
from database import db
from models import Patient, Doctor, Department, Appointment, Treatment, DoctorAvailability
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_
from utils.cache import cache_get_json, cache_set_json

patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')

@patient_bp.route('/dashboard', methods=['GET'])
@patient_required
def patient_dashboard(current_user):
    """
    Patient dashboard with departments, doctors, and appointments
    """
    try:
        patient = current_user.patient_profile
        
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        # Get all departments
        departments = Department.query.all()
        
        # Get upcoming appointments
        today = date.today()
        upcoming_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= today,
            Appointment.status.in_(['Booked', 'Completed'])
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        
        # Get past appointments with treatment
        past_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date < today
        ).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).limit(20).all()
        
        # Include treatment details
        appointments_with_treatment = []
        for apt in past_appointments:
            apt_dict = apt.to_dict()
            if apt.treatment:
                apt_dict['treatment'] = apt.treatment.to_dict()
            appointments_with_treatment.append(apt_dict)
        
        return jsonify({
            'role': 'patient',
            'patient': patient.to_dict(),
            'departments': [dept.to_dict() for dept in departments],
            'upcoming_appointments': [apt.to_dict() for apt in upcoming_appointments],
            'past_appointments': appointments_with_treatment,
            'statistics': {
                'upcoming_count': len(upcoming_appointments),
                'past_count': len(past_appointments),
                'total_departments': len(departments)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to load dashboard: {str(e)}'}), 500

# ==================== PROFILE MANAGEMENT ====================

@patient_bp.route('/profile', methods=['GET'])
@patient_required
def get_profile(current_user):
    """Get patient profile"""
    try:
        patient = current_user.patient_profile
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        return jsonify({'patient': patient.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@patient_bp.route('/profile', methods=['PUT'])
@patient_required
def update_profile(current_user):
    """
    Update patient profile
    """
    try:
        patient = current_user.patient_profile
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        data = request.get_json()
        
        # Update fields
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
        
        # Update user email if provided
        if 'email' in data and patient.user:
            from models import User
            email = data['email'].strip().lower()
            if User.query.filter(User.email == email, User.id != patient.user_id).first():
                return jsonify({'error': 'Email already registered'}), 400
            patient.user.email = email
        
        patient.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'patient': patient.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

# ==================== DOCTORS SEARCH ====================

DOCTOR_SEARCH_CACHE_TTL = 300  # 5 minutes


@patient_bp.route('/doctors', methods=['GET'])
@patient_required
def search_doctors(current_user):
    """
    Search and view doctors
    Query params: search (name), specialization_id, available_date
    """
    try:
        search = request.args.get('search', '').strip()
        specialization_id = request.args.get('specialization_id', type=int)
        available_date = request.args.get('available_date')  # YYYY-MM-DD
        
        query = Doctor.query.filter_by(is_active=True)
        
        # Filter by specialization
        if specialization_id:
            query = query.filter_by(specialization_id=specialization_id)
        
        # Search by name
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    Doctor.first_name.ilike(search_pattern),
                    Doctor.last_name.ilike(search_pattern)
                )
            )
        
        available_date_key = 'any'
        selected_date = None
        
        # Filter by availability if date provided
        if available_date:
            try:
                selected_date = datetime.strptime(available_date, '%Y-%m-%d').date()
                available_date_key = selected_date.isoformat()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        search_key = (
            f"doctors:search:"
            f"{search or 'all'}:"
            f"{specialization_id or 'any'}:"
            f"{available_date_key}"
        )
        cached_response = cache_get_json(search_key)
        if cached_response:
            return jsonify(cached_response), 200

        doctors = query.all()

        if selected_date:
            available_doctor_ids = db.session.query(DoctorAvailability.doctor_id).filter(
                DoctorAvailability.date == selected_date,
                DoctorAvailability.is_available == True
            ).distinct().all()
            available_doctor_ids = [did[0] for did in available_doctor_ids]
            
            doctors = [d for d in doctors if d.id in available_doctor_ids]

        # Get availability for each doctor (next 7 days)
        today = date.today()
        week_end = today + timedelta(days=7)
        
        doctors_with_availability = []
        for doctor in doctors:
            doctor_dict = doctor.to_dict()
            
            # Get availability for next 7 days
            availability = DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor.id,
                DoctorAvailability.date >= today,
                DoctorAvailability.date <= week_end,
                DoctorAvailability.is_available == True
            ).order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()
            
            doctor_dict['availability'] = [avail.to_dict() for avail in availability]
            doctors_with_availability.append(doctor_dict)
        
        response_payload = {
            'doctors': doctors_with_availability,
            'count': len(doctors_with_availability)
        }

        cache_set_json(search_key, response_payload, ttl=DOCTOR_SEARCH_CACHE_TTL)
        return jsonify(response_payload), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to search doctors: {str(e)}'}), 500

@patient_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@patient_required
def get_doctor_details(current_user, doctor_id):
    """
    Get detailed doctor information with availability
    """
    try:
        doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first_or_404()
        
        # Get availability for next 7 days
        today = date.today()
        week_end = today + timedelta(days=7)
        
        availability = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= week_end,
            DoctorAvailability.is_available == True
        ).order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()
        
        doctor_dict = doctor.to_dict()
        doctor_dict['availability'] = [avail.to_dict() for avail in availability]
        
        return jsonify({'doctor': doctor_dict}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get doctor details: {str(e)}'}), 500

# ==================== APPOINTMENTS ====================

@patient_bp.route('/appointments', methods=['GET'])
@patient_required
def get_appointments(current_user):
    """
    Get patient's appointments
    Query params: status, upcoming_only
    """
    try:
        patient = current_user.patient_profile
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        status = request.args.get('status')
        upcoming_only = request.args.get('upcoming_only', 'false').lower() == 'true'
        
        query = Appointment.query.filter_by(patient_id=patient.id)
        
        if status:
            query = query.filter_by(status=status)
        
        if upcoming_only:
            today = date.today()
            query = query.filter(Appointment.appointment_date >= today)
        
        appointments = query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        ).all()
        
        # Include treatment details
        appointments_with_treatment = []
        for apt in appointments:
            apt_dict = apt.to_dict()
            if apt.treatment:
                apt_dict['treatment'] = apt.treatment.to_dict()
            appointments_with_treatment.append(apt_dict)
        
        return jsonify({
            'appointments': appointments_with_treatment,
            'count': len(appointments_with_treatment)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get appointments: {str(e)}'}), 500

@patient_bp.route('/appointments', methods=['POST'])
@patient_required
def book_appointment(current_user):
    """
    Book a new appointment
    Required: doctor_id, appointment_date, appointment_time
    Optional: reason
    """
    try:
        patient = current_user.patient_profile
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('doctor_id') or not data.get('appointment_date') or not data.get('appointment_time'):
            return jsonify({'error': 'doctor_id, appointment_date, and appointment_time are required'}), 400
        
        doctor_id = data['doctor_id']
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        
        # Check if doctor exists and is active
        doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first()
        if not doctor:
            return jsonify({'error': 'Doctor not found or inactive'}), 404
        
        # Check if appointment date is in the past
        if appointment_date < date.today():
            return jsonify({'error': 'Cannot book appointment in the past'}), 400
        
        # Comprehensive validation using utility functions
        from utils.appointment_utils import validate_appointment_booking
        
        is_valid, error_message, conflict_details = validate_appointment_booking(
            doctor_id=doctor_id,
            patient_id=patient.id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )
        
        if not is_valid:
            response = {'error': error_message}
            if conflict_details:
                response['conflict_details'] = conflict_details
            return jsonify(response), 400
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='Booked',
            reason=data.get('reason', '').strip() or None
        )
        
        db.session.add(appointment)
        
        # Update doctor availability - mark the slot as unavailable
        from utils.cache import invalidate_doctor_availability_cache, invalidate_doctor_search_cache
        
        availability_slot = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date == appointment_date,
            DoctorAvailability.start_time <= appointment_time,
            DoctorAvailability.end_time >= appointment_time
        ).first()
        
        if availability_slot:
            availability_slot.is_available = False
            invalidate_doctor_availability_cache(doctor_id)
            invalidate_doctor_search_cache()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': appointment.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date/time format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to book appointment: {str(e)}'}), 500

@patient_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@patient_required
def reschedule_appointment(current_user, appointment_id):
    """
    Reschedule an appointment
    Required: appointment_date, appointment_time
    """
    try:
        patient = current_user.patient_profile
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient.id
        ).first_or_404()
        
        if appointment.status != 'Booked':
            return jsonify({'error': 'Only booked appointments can be rescheduled'}), 400
        
        data = request.get_json()
        
        if not data.get('appointment_date') or not data.get('appointment_time'):
            return jsonify({'error': 'appointment_date and appointment_time are required'}), 400
        
        new_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        new_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        
        # Check if new date is in the past
        if new_date < date.today():
            return jsonify({'error': 'Cannot reschedule to a past date'}), 400
        
        # Comprehensive validation using utility functions
        from utils.appointment_utils import validate_appointment_booking
        
        is_valid, error_message, conflict_details = validate_appointment_booking(
            doctor_id=appointment.doctor_id,
            patient_id=patient.id,
            appointment_date=new_date,
            appointment_time=new_time,
            exclude_appointment_id=appointment_id
        )
        
        if not is_valid:
            response = {'error': error_message}
            if conflict_details:
                response['conflict_details'] = conflict_details
            return jsonify(response), 400
        
        # Update appointment
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment rescheduled successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date/time format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to reschedule appointment: {str(e)}'}), 500

@patient_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@patient_required
def cancel_appointment(current_user, appointment_id):
    """
    Cancel an appointment
    """
    try:
        patient = current_user.patient_profile
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient.id
        ).first_or_404()
        
        # Validate status transition
        from utils.appointment_utils import can_transition_status
        
        if not can_transition_status(appointment.status, 'Cancelled'):
            return jsonify({
                'error': f'Cannot transition from {appointment.status} to Cancelled',
                'current_status': appointment.status,
                'valid_transitions': ['Completed', 'Cancelled'] if appointment.status == 'Booked' else []
            }), 400
        
        appointment.status = 'Cancelled'
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Appointment cancelled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to cancel appointment: {str(e)}'}), 500

@patient_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@patient_required
def get_appointment_details(current_user, appointment_id):
    """
    Get appointment details with treatment history
    """
    try:
        patient = current_user.patient_profile
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient.id
        ).first_or_404()
        
        apt_dict = appointment.to_dict()
        if appointment.treatment:
            apt_dict['treatment'] = appointment.treatment.to_dict()
        
        return jsonify({'appointment': apt_dict}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get appointment: {str(e)}'}), 500

# ==================== DEPARTMENTS ====================

@patient_bp.route('/departments', methods=['GET'])
@patient_required
def get_departments(current_user):
    """
    Get all departments with doctor counts
    """
    try:
        departments = Department.query.all()
        departments_with_counts = []
        
        for dept in departments:
            dept_dict = dept.to_dict()
            # Count active doctors in this department
            doctor_count = Doctor.query.filter_by(
                specialization_id=dept.id,
                is_active=True
            ).count()
            dept_dict['active_doctors_count'] = doctor_count
            departments_with_counts.append(dept_dict)
        
        return jsonify({
            'departments': departments_with_counts
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get departments: {str(e)}'}), 500

@patient_bp.route('/departments/<int:department_id>', methods=['GET'])
@patient_required
def get_department_details(current_user, department_id):
    """
    Get department details with list of doctors
    """
    try:
        department = Department.query.get_or_404(department_id)
        
        # Get doctors in this department
        doctors = Doctor.query.filter_by(
            specialization_id=department.id,
            is_active=True
        ).all()
        
        dept_dict = department.to_dict()
        dept_dict['doctors'] = [doc.to_dict() for doc in doctors]
        
        return jsonify({'department': dept_dict}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get department details: {str(e)}'}), 500


