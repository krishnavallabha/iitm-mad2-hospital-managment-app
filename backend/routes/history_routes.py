"""
Appointment and Treatment History Routes
Provides comprehensive history viewing for all roles
"""
from flask import Blueprint, request, jsonify
from auth import admin_required, doctor_required, patient_required, admin_or_doctor_required
from database import db
from models import Appointment, Treatment, Patient, Doctor
from datetime import date, datetime, timedelta
from sqlalchemy import and_, or_, desc

history_bp = Blueprint('history', __name__, url_prefix='/api/history')

# ==================== APPOINTMENT HISTORY ====================

@history_bp.route('/appointments', methods=['GET'])
@admin_required
def admin_appointment_history(current_user):
    """
    Admin: View complete appointment history with filters
    Query params: patient_id, doctor_id, status, date_from, date_to, include_treatment
    """
    try:
        patient_id = request.args.get('patient_id', type=int)
        doctor_id = request.args.get('doctor_id', type=int)
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        include_treatment = request.args.get('include_treatment', 'true').lower() == 'true'
        
        query = Appointment.query
        
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)
        
        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)
        
        appointments = query.order_by(
            desc(Appointment.appointment_date),
            desc(Appointment.appointment_time)
        ).all()
        
        # Build response with treatment details if requested
        appointments_data = []
        for apt in appointments:
            apt_dict = apt.to_dict()
            if include_treatment and apt.treatment:
                apt_dict['treatment'] = apt.treatment.to_dict()
            appointments_data.append(apt_dict)
        
        return jsonify({
            'appointments': appointments_data,
            'count': len(appointments_data),
            'filters': {
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'status': status,
                'date_from': date_from,
                'date_to': date_to
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get appointment history: {str(e)}'}), 500

@history_bp.route('/appointments/patient/<int:patient_id>', methods=['GET'])
@admin_or_doctor_required
def view_patient_appointment_history(current_user, patient_id):
    """
    Admin/Doctor: View complete appointment history for a specific patient
    """
    try:
        # Verify patient exists
        patient = Patient.query.get_or_404(patient_id)
        
        # If doctor, verify they have treated this patient
        if current_user.role == 'doctor':
            doctor = current_user.doctor_profile
            if not doctor:
                return jsonify({'error': 'Doctor profile not found'}), 404
            
            # Check if doctor has any appointments with this patient
            has_relation = Appointment.query.filter_by(
                doctor_id=doctor.id,
                patient_id=patient_id
            ).first()
            
            if not has_relation:
                return jsonify({
                    'error': 'You do not have access to this patient\'s history',
                    'message': 'You must have at least one appointment with this patient'
                }), 403
        
        # Get all appointments for this patient
        appointments = Appointment.query.filter_by(
            patient_id=patient_id
        ).order_by(
            desc(Appointment.appointment_date),
            desc(Appointment.appointment_time)
        ).all()
        
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
            'total_appointments': len(appointments_with_treatment),
            'statistics': {
                'booked': len([a for a in appointments if a.status == 'Booked']),
                'completed': len([a for a in appointments if a.status == 'Completed']),
                'cancelled': len([a for a in appointments if a.status == 'Cancelled']),
                'with_treatment': len([a for a in appointments if a.treatment])
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get patient history: {str(e)}'}), 500

@history_bp.route('/appointments/my-history', methods=['GET'])
@patient_required
def patient_own_history(current_user):
    """
    Patient: View own complete appointment and treatment history
    Query params: status, date_from, date_to
    """
    try:
        patient = current_user.patient_profile
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Appointment.query.filter_by(patient_id=patient.id)
        
        if status:
            query = query.filter_by(status=status)
        
        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)
        
        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)
        
        appointments = query.order_by(
            desc(Appointment.appointment_date),
            desc(Appointment.appointment_time)
        ).all()
        
        # Include all treatment details
        appointments_with_treatment = []
        for apt in appointments:
            apt_dict = apt.to_dict()
            if apt.treatment:
                apt_dict['treatment'] = apt.treatment.to_dict()
            appointments_with_treatment.append(apt_dict)
        
        # Calculate statistics
        today = date.today()
        upcoming = [a for a in appointments if a.appointment_date >= today and a.status == 'Booked']
        past = [a for a in appointments if a.appointment_date < today or a.status in ['Completed', 'Cancelled']]
        
        return jsonify({
            'patient': patient.to_dict(),
            'appointments': appointments_with_treatment,
            'total_appointments': len(appointments_with_treatment),
            'statistics': {
                'total': len(appointments),
                'upcoming': len(upcoming),
                'past': len(past),
                'booked': len([a for a in appointments if a.status == 'Booked']),
                'completed': len([a for a in appointments if a.status == 'Completed']),
                'cancelled': len([a for a in appointments if a.status == 'Cancelled']),
                'with_treatment': len([a for a in appointments if a.treatment])
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get appointment history: {str(e)}'}), 500

# ==================== TREATMENT HISTORY ====================

@history_bp.route('/treatments', methods=['GET'])
@admin_required
def admin_treatment_history(current_user):
    """
    Admin: View all treatment records
    Query params: patient_id, doctor_id, date_from, date_to
    """
    try:
        patient_id = request.args.get('patient_id', type=int)
        doctor_id = request.args.get('doctor_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Treatment.query.join(Appointment)
        
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        
        if date_from:
            query = query.filter(Appointment.appointment_date >= date_from)
        
        if date_to:
            query = query.filter(Appointment.appointment_date <= date_to)
        
        treatments = query.order_by(
            desc(Appointment.appointment_date)
        ).all()
        
        treatments_data = []
        for treatment in treatments:
            treatment_dict = treatment.to_dict()
            if treatment.appointment:
                treatment_dict['appointment'] = treatment.appointment.to_dict()
            treatments_data.append(treatment_dict)
        
        return jsonify({
            'treatments': treatments_data,
            'count': len(treatments_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get treatment history: {str(e)}'}), 500

@history_bp.route('/treatments/patient/<int:patient_id>', methods=['GET'])
@admin_or_doctor_required
def view_patient_treatment_history(current_user, patient_id):
    """
    Admin/Doctor: View all treatment records for a specific patient
    """
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # If doctor, verify access
        if current_user.role == 'doctor':
            doctor = current_user.doctor_profile
            if not doctor:
                return jsonify({'error': 'Doctor profile not found'}), 404
            
            # Check if doctor has treated this patient
            has_relation = Appointment.query.filter_by(
                doctor_id=doctor.id,
                patient_id=patient_id
            ).first()
            
            if not has_relation:
                return jsonify({'error': 'You do not have access to this patient\'s treatment history'}), 403
        
        # Get all treatments for this patient
        treatments = Treatment.query.join(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(
            desc(Appointment.appointment_date)
        ).all()
        
        treatments_data = []
        for treatment in treatments:
            treatment_dict = treatment.to_dict()
            if treatment.appointment:
                apt_dict = treatment.appointment.to_dict()
                # Include doctor info
                if treatment.appointment.doctor:
                    apt_dict['doctor'] = treatment.appointment.doctor.to_dict()
                treatment_dict['appointment'] = apt_dict
            treatments_data.append(treatment_dict)
        
        return jsonify({
            'patient': patient.to_dict(),
            'treatments': treatments_data,
            'count': len(treatments_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get treatment history: {str(e)}'}), 500

@history_bp.route('/treatments/my-treatments', methods=['GET'])
@patient_required
def patient_own_treatments(current_user):
    """
    Patient: View own treatment records
    """
    try:
        patient = current_user.patient_profile
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        # Get all treatments for this patient
        treatments = Treatment.query.join(Appointment).filter(
            Appointment.patient_id == patient.id
        ).order_by(
            desc(Appointment.appointment_date)
        ).all()
        
        treatments_data = []
        for treatment in treatments:
            treatment_dict = treatment.to_dict()
            if treatment.appointment:
                apt_dict = treatment.appointment.to_dict()
                # Include doctor info
                if treatment.appointment.doctor:
                    apt_dict['doctor'] = treatment.appointment.doctor.to_dict()
                treatment_dict['appointment'] = apt_dict
            treatments_data.append(treatment_dict)
        
        return jsonify({
            'treatments': treatments_data,
            'count': len(treatments_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get treatment history: {str(e)}'}), 500

# ==================== STATUS STATISTICS ====================

@history_bp.route('/statistics', methods=['GET'])
@admin_required
def appointment_statistics(current_user):
    """
    Admin: Get appointment statistics by status
    """
    try:
        from sqlalchemy import func
        
        # Get counts by status
        status_counts = db.session.query(
            Appointment.status,
            func.count(Appointment.id).label('count')
        ).group_by(Appointment.status).all()
        
        # Get total counts
        total_appointments = Appointment.query.count()
        total_with_treatment = Treatment.query.count()
        
        # Get recent activity (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_appointments = Appointment.query.filter(
            Appointment.appointment_date >= thirty_days_ago
        ).count()
        
        statistics = {
            'total_appointments': total_appointments,
            'total_with_treatment': total_with_treatment,
            'recent_appointments_30_days': recent_appointments,
            'by_status': {status: count for status, count in status_counts}
        }
        
        return jsonify({'statistics': statistics}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

