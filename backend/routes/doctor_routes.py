"""
Doctor routes for managing appointments, treatments, and availability
"""
from flask import Blueprint, request, jsonify
from auth import doctor_required
from database import db
from models import Doctor, Patient, Appointment, Treatment, DoctorAvailability
from datetime import datetime, date, timedelta
from sqlalchemy import and_
from utils.cache import (
    cache_get_json,
    cache_set_json,
    invalidate_doctor_availability_cache,
    invalidate_doctor_search_cache,
)

doctor_bp = Blueprint('doctor', __name__, url_prefix='/api/doctor')

@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def doctor_dashboard(current_user):
    """
    Doctor dashboard with appointments and statistics
    """
    try:
        doctor = current_user.doctor_profile
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        today = date.today()
        week_end = today + timedelta(days=7)
        
        # Today's appointments
        today_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today,
            Appointment.status == 'Booked'
        ).order_by(Appointment.appointment_time).all()
        
        # Upcoming appointments (next 7 days)
        upcoming_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= today,
            Appointment.appointment_date <= week_end,
            Appointment.status == 'Booked'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        
        # Completed today
        completed_today = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today,
            Appointment.status == 'Completed'
        ).count()
        
        # Assigned patients (unique patients with appointments)
        patient_ids = db.session.query(Appointment.patient_id).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().all()
        patient_ids = [pid[0] for pid in patient_ids]
        assigned_patients = Patient.query.filter(Patient.id.in_(patient_ids)).limit(20).all()
        
        # Statistics
        total_appointments = Appointment.query.filter_by(doctor_id=doctor.id).count()
        completed_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == 'Completed'
        ).count()
        
        return jsonify({
            'role': 'doctor',
            'doctor': doctor.to_dict(),
            'statistics': {
                'appointments_today': len(today_appointments),
                'completed_today': completed_today,
                'upcoming_this_week': len(upcoming_appointments),
                'total_patients': len(assigned_patients),
                'total_appointments': total_appointments,
                'completed_appointments': completed_appointments
            },
            'today_appointments': [apt.to_dict() for apt in today_appointments],
            'upcoming_appointments': [apt.to_dict() for apt in upcoming_appointments],
            'assigned_patients': [patient.to_dict() for patient in assigned_patients]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to load dashboard: {str(e)}'}), 500

# ==================== APPOINTMENTS ====================

@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments(current_user):
    """
    Get doctor's appointments with optional filters
    Query params: status, date_from, date_to
    """
    try:
        doctor = current_user.doctor_profile
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Appointment.query.filter_by(doctor_id=doctor.id)
        
        if status:
            query = query.filter_by(status=status)
        
        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)
        
        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)
        
        appointments = query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        ).all()
        
        # Include treatment data in appointments
        appointments_data = []
        for apt in appointments:
            apt_dict = apt.to_dict()
            if apt.treatment:
                apt_dict['treatment'] = apt.treatment.to_dict()
            appointments_data.append(apt_dict)
        
        return jsonify({
            'appointments': appointments_data,
            'count': len(appointments_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get appointments: {str(e)}'}), 500

@doctor_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@doctor_required
def get_appointment(current_user, appointment_id):
    """Get appointment details"""
    try:
        doctor = current_user.doctor_profile
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id
        ).first_or_404()
        
        apt_dict = appointment.to_dict()
        if appointment.treatment:
            apt_dict['treatment'] = appointment.treatment.to_dict()
        
        return jsonify({'appointment': apt_dict}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get appointment: {str(e)}'}), 500

@doctor_bp.route('/appointments/<int:appointment_id>/complete', methods=['PUT'])
@doctor_required
def complete_appointment(current_user, appointment_id):
    """
    Mark appointment as completed
    """
    try:
        doctor = current_user.doctor_profile
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id
        ).first_or_404()
        
        # Validate status transition
        from utils.appointment_utils import can_transition_status
        
        if not can_transition_status(appointment.status, 'Completed'):
            return jsonify({
                'error': f'Cannot transition from {appointment.status} to Completed',
                'current_status': appointment.status,
                'valid_transitions': ['Completed', 'Cancelled'] if appointment.status == 'Booked' else []
            }), 400
        
        appointment.status = 'Completed'
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment marked as completed',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to complete appointment: {str(e)}'}), 500

@doctor_bp.route('/appointments/<int:appointment_id>/cancel', methods=['PUT'])
@doctor_required
def cancel_appointment(current_user, appointment_id):
    """
    Cancel appointment
    """
    try:
        doctor = current_user.doctor_profile
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id
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
        
        return jsonify({
            'message': 'Appointment cancelled successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to cancel appointment: {str(e)}'}), 500

# ==================== TREATMENTS ====================

@doctor_bp.route('/appointments/<int:appointment_id>/treatment', methods=['POST'])
@doctor_required
def add_treatment(current_user, appointment_id):
    """
    Add treatment record to appointment
    Required: diagnosis
    Optional: prescription, notes, follow_up_date, follow_up_notes
    """
    try:
        doctor = current_user.doctor_profile
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id
        ).first_or_404()
        
        # Check if treatment already exists
        if appointment.treatment:
            return jsonify({'error': 'Treatment already exists for this appointment. Use PUT to update.'}), 400
        
        data = request.get_json()
        
        if not data.get('diagnosis'):
            return jsonify({'error': 'Diagnosis is required'}), 400
        
        # Helper function to safely strip strings
        def safe_strip(value):
            if value is None:
                return None
            if isinstance(value, str):
                stripped = value.strip()
                return stripped if stripped else None
            return value
        
        treatment = Treatment(
            appointment_id=appointment_id,
            diagnosis=data['diagnosis'].strip(),
            prescription=safe_strip(data.get('prescription')),
            notes=safe_strip(data.get('notes')),
            follow_up_date=data.get('follow_up_date') or None,
            follow_up_notes=safe_strip(data.get('follow_up_notes')),
            tests_done=safe_strip(data.get('tests_done')),
            medicines=safe_strip(data.get('medicines')),
            attachments=data.get('attachments') if data.get('attachments') else None
        )
        
        db.session.add(treatment)
        
        # Mark appointment as completed if not already
        if appointment.status == 'Booked':
            appointment.status = 'Completed'
            appointment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Treatment added successfully',
            'treatment': treatment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add treatment: {str(e)}'}), 500

@doctor_bp.route('/appointments/<int:appointment_id>/treatment', methods=['PUT'])
@doctor_required
def update_treatment(current_user, appointment_id):
    """
    Update treatment record
    """
    try:
        doctor = current_user.doctor_profile
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id
        ).first_or_404()
        
        if not appointment.treatment:
            return jsonify({'error': 'Treatment not found. Use POST to create.'}), 404
        
        treatment = appointment.treatment
        data = request.get_json()
        
        # Helper function to safely strip strings
        def safe_strip(value):
            if value is None:
                return None
            if isinstance(value, str):
                stripped = value.strip()
                return stripped if stripped else None
            return value
        
        if 'diagnosis' in data and data['diagnosis']:
            treatment.diagnosis = data['diagnosis'].strip()
        if 'prescription' in data:
            treatment.prescription = safe_strip(data.get('prescription'))
        if 'notes' in data:
            treatment.notes = safe_strip(data.get('notes'))
        if 'follow_up_date' in data:
            treatment.follow_up_date = data['follow_up_date'] if data['follow_up_date'] else None
        if 'follow_up_notes' in data:
            treatment.follow_up_notes = safe_strip(data.get('follow_up_notes'))
        if 'tests_done' in data:
            treatment.tests_done = safe_strip(data.get('tests_done'))
        if 'medicines' in data:
            treatment.medicines = safe_strip(data.get('medicines'))
        if 'attachments' in data:
            treatment.attachments = data['attachments'] if data['attachments'] else None
        if 'visit_type' in data:
            appointment.visit_type = data['visit_type']
        
        treatment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Treatment updated successfully',
            'treatment': treatment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update treatment: {str(e)}'}), 500

# ==================== PATIENT HISTORY ====================

@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_assigned_patients(current_user):
    """
    Get list of patients assigned to this doctor with latest diagnosis
    """
    try:
        doctor = current_user.doctor_profile
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        # Get unique patient IDs
        patient_ids = db.session.query(Appointment.patient_id).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().all()
        patient_ids = [pid[0] for pid in patient_ids]
        
        patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
        
        # Get latest diagnosis for each patient from completed appointments
        from models import Treatment
        patients_with_diagnosis = []
        for patient in patients:
            patient_dict = patient.to_dict()
            
            # Get the most recent completed appointment with treatment for this patient and doctor
            latest_appointment = Appointment.query.filter(
                Appointment.patient_id == patient.id,
                Appointment.doctor_id == doctor.id,
                Appointment.status == 'Completed'
            ).order_by(
                Appointment.appointment_date.desc(),
                Appointment.appointment_time.desc()
            ).first()
            
            # Get the latest diagnosis from treatment
            if latest_appointment and latest_appointment.treatment:
                patient_dict['latest_diagnosis'] = latest_appointment.treatment.diagnosis
            else:
                patient_dict['latest_diagnosis'] = None
            
            patients_with_diagnosis.append(patient_dict)
        
        return jsonify({
            'patients': patients_with_diagnosis,
            'count': len(patients_with_diagnosis)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get patients: {str(e)}'}), 500

@doctor_bp.route('/patients/<int:patient_id>', methods=['GET'])
@doctor_required
def get_patient_history(current_user, patient_id):
    """
    Get full medical history of a patient
    Shows all appointments and treatments with this doctor
    """
    try:
        doctor = current_user.doctor_profile
        patient = Patient.query.get_or_404(patient_id)
        
        # Get all appointments with this doctor
        appointments = Appointment.query.filter_by(
            patient_id=patient_id,
            doctor_id=doctor.id
        ).order_by(Appointment.appointment_date.desc()).all()
        
        # Include treatment details
        appointments_with_treatment = []
        for apt in appointments:
            apt_dict = apt.to_dict()
            if apt.treatment:
                apt_dict['treatment'] = apt.treatment.to_dict()
            appointments_with_treatment.append(apt_dict)
        
        return jsonify({
            'patient': patient.to_dict(),
            'appointments': appointments_with_treatment,
            'total_appointments': len(appointments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get patient history: {str(e)}'}), 500

# ==================== AVAILABILITY ====================

AVAILABILITY_CACHE_TTL = 300  # 5 minutes


@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability(current_user):
    """
    Get doctor's availability for next 7 days
    """
    try:
        doctor = current_user.doctor_profile
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        cache_key = f"doctor:availability:{doctor.id}"
        cached = cache_get_json(cache_key)
        if cached:
            return jsonify(cached), 200
        
        today = date.today()
        week_end = today + timedelta(days=7)
        
        availability = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= week_end
        ).order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()
        
        response_payload = {
            'availability': [avail.to_dict() for avail in availability],
            'count': len(availability)
        }
        
        cache_set_json(cache_key, response_payload, ttl=AVAILABILITY_CACHE_TTL)
        return jsonify(response_payload), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get availability: {str(e)}'}), 500

@doctor_bp.route('/availability', methods=['POST'])
@doctor_required
def set_availability(current_user):
    """
    Set availability slots for next 7 days
    Body: Array of availability objects
    [
      {
        "date": "YYYY-MM-DD",
        "start_time": "HH:MM",
        "end_time": "HH:MM",
        "is_available": true
      }
    ]
    """
    try:
        doctor = current_user.doctor_profile
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'error': 'Expected array of availability objects'}), 400
        
        today = date.today()
        week_end = today + timedelta(days=7)
        
        # Clear existing availability for next 7 days
        DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= week_end
        ).delete()
        
        # Add new availability slots
        created_slots = []
        for slot_data in data:
            slot_date = datetime.strptime(slot_data['date'], '%Y-%m-%d').date()
            
            # Only allow setting availability for next 7 days
            if slot_date < today or slot_date > week_end:
                continue
            
            slot = DoctorAvailability(
                doctor_id=doctor.id,
                date=slot_date,
                start_time=datetime.strptime(slot_data['start_time'], '%H:%M').time(),
                end_time=datetime.strptime(slot_data['end_time'], '%H:%M').time(),
                is_available=slot_data.get('is_available', True)
            )
            
            db.session.add(slot)
            created_slots.append(slot)
        
        db.session.commit()
        invalidate_doctor_availability_cache(doctor.id)
        invalidate_doctor_search_cache()
        
        return jsonify({
            'message': f'Availability updated successfully. Created {len(created_slots)} slots.',
            'availability': [slot.to_dict() for slot in created_slots]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update availability: {str(e)}'}), 500

@doctor_bp.route('/availability/<int:availability_id>', methods=['PUT'])
@doctor_required
def update_availability_slot(current_user, availability_id):
    """
    Update a specific availability slot
    """
    try:
        doctor = current_user.doctor_profile
        availability = DoctorAvailability.query.filter_by(
            id=availability_id,
            doctor_id=doctor.id
        ).first_or_404()
        
        data = request.get_json()
        
        if 'start_time' in data:
            availability.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        if 'end_time' in data:
            availability.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        if 'is_available' in data:
            availability.is_available = bool(data['is_available'])
        
        db.session.commit()
        invalidate_doctor_availability_cache(doctor.id)
        invalidate_doctor_search_cache()
        
        return jsonify({
            'message': 'Availability slot updated successfully',
            'availability': availability.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update availability: {str(e)}'}), 500

@doctor_bp.route('/availability/<int:availability_id>', methods=['DELETE'])
@doctor_required
def delete_availability_slot(current_user, availability_id):
    """
    Delete an availability slot
    """
    try:
        doctor = current_user.doctor_profile
        availability = DoctorAvailability.query.filter_by(
            id=availability_id,
            doctor_id=doctor.id
        ).first_or_404()
        
        db.session.delete(availability)
        db.session.commit()
        invalidate_doctor_availability_cache(doctor.id)
        invalidate_doctor_search_cache()
        
        return jsonify({'message': 'Availability slot deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete availability: {str(e)}'}), 500

