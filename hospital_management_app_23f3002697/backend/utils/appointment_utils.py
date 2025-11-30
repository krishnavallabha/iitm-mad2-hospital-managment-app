"""
Utility functions for appointment conflict prevention and validation
"""
from database import db
from models import Appointment, DoctorAvailability
from datetime import date, time, datetime
from sqlalchemy import and_

def check_appointment_conflict(doctor_id, appointment_date, appointment_time, exclude_appointment_id=None):
    """
    Check if there's a conflict for a doctor at a specific date and time
    Returns: (has_conflict: bool, conflict_appointment: Appointment or None, error_message: str or None)
    """
    try:
        # Check if doctor has another booked appointment at the same time
        query = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status == 'Booked'
        )
        
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
        
        conflict = query.first()
        
        if conflict:
            return True, conflict, f"Doctor already has a booked appointment at {appointment_time} on {appointment_date}"
        
        return False, None, None
        
    except Exception as e:
        return True, None, f"Error checking conflict: {str(e)}"

def check_patient_conflict(patient_id, appointment_date, appointment_time, exclude_appointment_id=None):
    """
    Check if patient already has an appointment at the same time
    Returns: (has_conflict: bool, conflict_appointment: Appointment or None, error_message: str or None)
    """
    try:
        query = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status == 'Booked'
        )
        
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
        
        conflict = query.first()
        
        if conflict:
            return True, conflict, f"Patient already has a booked appointment at {appointment_time} on {appointment_date}"
        
        return False, None, None
        
    except Exception as e:
        return True, None, f"Error checking conflict: {str(e)}"

def check_doctor_availability(doctor_id, appointment_date, appointment_time):
    """
    Check if doctor has availability set for the given date and time
    Returns: (is_available: bool, availability_slot: DoctorAvailability or None, error_message: str or None)
    """
    try:
        availability = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date == appointment_date,
            DoctorAvailability.start_time <= appointment_time,
            DoctorAvailability.end_time >= appointment_time,
            DoctorAvailability.is_available == True
        ).first()
        
        if not availability:
            return False, None, f"Doctor does not have availability set for {appointment_time} on {appointment_date}"
        
        return True, availability, None
        
    except Exception as e:
        return False, None, f"Error checking availability: {str(e)}"

def validate_appointment_booking(doctor_id, patient_id, appointment_date, appointment_time, exclude_appointment_id=None):
    """
    Comprehensive validation for appointment booking
    Checks:
    1. Doctor availability
    2. Doctor conflict (double booking)
    3. Patient conflict (patient double booking)
    
    Returns: (is_valid: bool, error_message: str or None, conflict_details: dict or None)
    """
    errors = []
    conflict_details = {}
    
    # Check if date is in the past
    if appointment_date < date.today():
        return False, "Cannot book appointment in the past", None
    
    # Check doctor availability
    is_available, availability_slot, avail_error = check_doctor_availability(
        doctor_id, appointment_date, appointment_time
    )
    if not is_available:
        errors.append(avail_error)
        conflict_details['availability'] = False
    
    # Check doctor conflict
    has_conflict, conflict_apt, conflict_error = check_appointment_conflict(
        doctor_id, appointment_date, appointment_time, exclude_appointment_id
    )
    if has_conflict:
        errors.append(conflict_error)
        conflict_details['doctor_conflict'] = {
            'appointment_id': conflict_apt.id if conflict_apt else None,
            'message': conflict_error
        }
    
    # Check patient conflict
    has_patient_conflict, patient_conflict_apt, patient_error = check_patient_conflict(
        patient_id, appointment_date, appointment_time, exclude_appointment_id
    )
    if has_patient_conflict:
        errors.append(patient_error)
        conflict_details['patient_conflict'] = {
            'appointment_id': patient_conflict_apt.id if patient_conflict_apt else None,
            'message': patient_error
        }
    
    if errors:
        return False, "; ".join(errors), conflict_details
    
    return True, None, None

def get_appointment_status_transitions():
    """
    Define valid status transitions
    Returns: dict mapping current status to list of valid next statuses
    """
    return {
        'Booked': ['Completed', 'Cancelled'],
        'Completed': [],  # Cannot change from completed
        'Cancelled': []   # Cannot change from cancelled
    }

def can_transition_status(current_status, new_status):
    """
    Check if status transition is valid
    """
    transitions = get_appointment_status_transitions()
    valid_next_statuses = transitions.get(current_status, [])
    return new_status in valid_next_statuses

def get_available_time_slots(doctor_id, appointment_date):
    """
    Get available time slots for a doctor on a specific date
    Returns: list of available time slots
    """
    try:
        # Get doctor's availability for the date
        availability_slots = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date == appointment_date,
            DoctorAvailability.is_available == True
        ).all()
        
        # Get booked appointments for the date
        booked_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status == 'Booked'
        ).all()
        
        booked_times = {apt.appointment_time for apt in booked_appointments}
        
        # Calculate available slots
        available_slots = []
        for slot in availability_slots:
            # Generate time slots within the availability window (assuming 30-minute intervals)
            current_time = slot.start_time
            while current_time < slot.end_time:
                if current_time not in booked_times:
                    available_slots.append({
                        'time': current_time.strftime('%H:%M'),
                        'available': True
                    })
                
                # Add 30 minutes
                current_datetime = datetime.combine(date.today(), current_time)
                current_datetime = current_datetime.replace(minute=current_datetime.minute + 30)
                current_time = current_datetime.time()
        
        return available_slots
        
    except Exception as e:
        return []

