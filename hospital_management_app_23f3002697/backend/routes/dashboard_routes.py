"""
Dashboard routes for different user roles
These routes demonstrate role-based access control
"""
from flask import Blueprint, jsonify
from auth import admin_required, doctor_required, patient_required, get_current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Doctor, Patient, Appointment, Department
from datetime import datetime, date, timedelta
from database import db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/admin', methods=['GET'])
@admin_required
def admin_dashboard(current_user):
    """
    Admin dashboard - shows statistics and overview
    Access: Admin only
    """
    try:
        # Get statistics
        total_doctors = Doctor.query.filter_by(is_active=True).count()
        total_patients = Patient.query.filter_by(is_active=True).count()
        total_appointments = Appointment.query.count()
        upcoming_appointments = Appointment.query.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.status == 'Booked'
        ).count()
        completed_appointments = Appointment.query.filter_by(status='Completed').count()
        
        # Get recent appointments
        recent_appointments = Appointment.query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        ).limit(10).all()
        
        return jsonify({
            'role': 'admin',
            'dashboard': 'admin',
            'statistics': {
                'total_doctors': total_doctors,
                'total_patients': total_patients,
                'total_appointments': total_appointments,
                'upcoming_appointments': upcoming_appointments,
                'completed_appointments': completed_appointments
            },
            'recent_appointments': [apt.to_dict() for apt in recent_appointments],
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to load admin dashboard: {str(e)}'}), 500

@dashboard_bp.route('/doctor', methods=['GET'])
@doctor_required
def doctor_dashboard(current_user):
    """
    Doctor dashboard - shows doctor's appointments and patients
    Access: Doctor only
    """
    try:
        doctor = current_user.doctor_profile
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        # Get today's appointments
        today = date.today()
        today_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today,
            Appointment.status == 'Booked'
        ).order_by(Appointment.appointment_time).all()
        
        # Get upcoming appointments (next 7 days)
        week_end = today + timedelta(days=7)
        upcoming_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= today,
            Appointment.appointment_date <= week_end,
            Appointment.status == 'Booked'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        
        # Get assigned patients (patients who have appointments with this doctor)
        patient_ids = db.session.query(Appointment.patient_id).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().all()
        patient_ids = [pid[0] for pid in patient_ids]
        assigned_patients = Patient.query.filter(Patient.id.in_(patient_ids)).limit(20).all()
        
        # Get completed appointments count for today
        completed_today = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today,
            Appointment.status == 'Completed'
        ).count()
        
        return jsonify({
            'role': 'doctor',
            'dashboard': 'doctor',
            'doctor': doctor.to_dict(),
            'statistics': {
                'appointments_today': len(today_appointments),
                'completed_today': completed_today,
                'upcoming_this_week': len(upcoming_appointments),
                'total_patients': len(assigned_patients)
            },
            'today_appointments': [apt.to_dict() for apt in today_appointments],
            'upcoming_appointments': [apt.to_dict() for apt in upcoming_appointments],
            'assigned_patients': [patient.to_dict() for patient in assigned_patients],
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to load doctor dashboard: {str(e)}'}), 500

@dashboard_bp.route('/patient', methods=['GET'])
@patient_required
def patient_dashboard(current_user):
    """
    Patient dashboard - shows available departments, doctors, and patient's appointments
    Access: Patient only
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
        
        # Get past appointments with treatment history
        past_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date < today
        ).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).limit(10).all()
        
        # Get appointments with treatment details
        appointments_with_treatment = []
        for apt in past_appointments:
            apt_dict = apt.to_dict()
            if apt.treatment:
                apt_dict['treatment'] = apt.treatment.to_dict()
            appointments_with_treatment.append(apt_dict)
        
        return jsonify({
            'role': 'patient',
            'dashboard': 'patient',
            'patient': patient.to_dict(),
            'departments': [dept.to_dict() for dept in departments],
            'upcoming_appointments': [apt.to_dict() for apt in upcoming_appointments],
            'past_appointments': appointments_with_treatment,
            'statistics': {
                'upcoming_count': len(upcoming_appointments),
                'past_count': len(past_appointments),
                'total_departments': len(departments)
            },
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to load patient dashboard: {str(e)}'}), 500

@dashboard_bp.route('/redirect', methods=['GET'])
@jwt_required()
def get_dashboard_redirect():
    """
    Returns the appropriate dashboard URL based on user role
    This helps the frontend redirect users after login
    """
    try:
        user_id = get_jwt_identity()
        # Convert string identity to int for database query
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        role = user.role
        dashboard_urls = {
            'admin': '/api/dashboard/admin',
            'doctor': '/api/dashboard/doctor',
            'patient': '/api/dashboard/patient'
        }
        
        return jsonify({
            'role': role,
            'dashboard_url': dashboard_urls.get(role, '/api/dashboard/patient'),
            'redirect_to': dashboard_urls.get(role, '/api/dashboard/patient')
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get dashboard redirect: {str(e)}'}), 500

