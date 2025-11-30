"""
Daily reminder tasks for appointments
"""
from celery_app import celery_app

from database import db
from models import Appointment, Patient, Doctor, User
from datetime import date, datetime
from utils.notifications import send_email_notification, send_gchat_notification, send_sms_notification
import logging

# Create app instance for Celery
@celery_app.task(name='tasks.reminder_tasks.send_daily_appointment_reminders', bind=True)
def send_daily_appointment_reminders(self):
    """
    Daily task to send reminders to patients with appointments today
    Runs at 8:00 AM daily
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        try:
            today = date.today()
            
            # Get all booked appointments for today
            appointments = Appointment.query.filter(
                Appointment.appointment_date == today,
                Appointment.status == 'Booked'
            ).all()
            
            logger.info(f"Found {len(appointments)} appointments for today")
            
            reminders_sent = 0
            reminders_failed = 0
            
            for appointment in appointments:
                try:
                    patient = appointment.patient
                    doctor = appointment.doctor
                    
                    if not patient or not patient.user:
                        logger.warning(f"Patient or user not found for appointment {appointment.id}")
                        continue
                    
                    # Prepare reminder message
                    appointment_time = appointment.appointment_time.strftime('%I:%M %p')
                    message = f"""
Dear {patient.first_name} {patient.last_name},

This is a reminder that you have an appointment scheduled today:

Date: {today.strftime('%B %d, %Y')}
Time: {appointment_time}
Doctor: Dr. {doctor.first_name} {doctor.last_name}
Department: {doctor.department.name if doctor.department else 'N/A'}

Please arrive 15 minutes before your scheduled time.

Thank you,
Hospital Management System
"""
                    
                    # Send via email (primary method)
                    email_sent = False
                    if patient.user.email:
                        try:
                            send_email_notification(
                                to_email=patient.user.email,
                                subject=f"Appointment Reminder - {today.strftime('%B %d, %Y')}",
                                message=message
                            )
                            email_sent = True
                            logger.info(f"Email reminder sent to {patient.user.email} for appointment {appointment.id}")
                        except Exception as e:
                            logger.error(f"Failed to send email to {patient.user.email}: {str(e)}")
                    
                    # Send via Google Chat (if webhook configured)
                    try:
                        send_gchat_notification(
                            message=f"Reminder: You have an appointment today at {appointment_time} with Dr. {doctor.first_name} {doctor.last_name}"
                        )
                    except Exception as e:
                        logger.warning(f"GChat notification failed (may not be configured): {str(e)}")
                    
                    # Send via SMS (if phone number available)
                    if patient.phone:
                        try:
                            send_sms_notification(
                                to_phone=patient.phone,
                                message=f"Reminder: Appointment today at {appointment_time} with Dr. {doctor.first_name} {doctor.last_name}"
                            )
                        except Exception as e:
                            logger.warning(f"SMS notification failed (may not be configured): {str(e)}")
                    
                    if email_sent:
                        reminders_sent += 1
                    else:
                        reminders_failed += 1
                        
                except Exception as e:
                    logger.error(f"Error processing appointment {appointment.id}: {str(e)}")
                    reminders_failed += 1
                    continue
            
            result = {
                'status': 'completed',
                'date': today.isoformat(),
                'total_appointments': len(appointments),
                'reminders_sent': reminders_sent,
                'reminders_failed': reminders_failed
            }
            
            logger.info(f"Daily reminders completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in daily reminder task: {str(e)}")
            raise

@celery_app.task(name='tasks.reminder_tasks.send_appointment_reminder', bind=True)
def send_appointment_reminder(self, appointment_id):
    """
    Send reminder for a specific appointment
    Can be triggered manually
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        try:
            appointment = Appointment.query.get(appointment_id)
            
            if not appointment:
                return {'status': 'error', 'message': 'Appointment not found'}
            
            patient = appointment.patient
            doctor = appointment.doctor
            
            if not patient or not patient.user:
                return {'status': 'error', 'message': 'Patient or user not found'}
            
            appointment_time = appointment.appointment_time.strftime('%I:%M %p')
            message = f"""
Dear {patient.first_name} {patient.last_name},

This is a reminder about your appointment:

Date: {appointment.appointment_date.strftime('%B %d, %Y')}
Time: {appointment_time}
Doctor: Dr. {doctor.first_name} {doctor.last_name}

Please arrive 15 minutes before your scheduled time.

Thank you,
Hospital Management System
"""
            
            # Send email
            if patient.user.email:
                send_email_notification(
                    to_email=patient.user.email,
                    subject=f"Appointment Reminder - {appointment.appointment_date.strftime('%B %d, %Y')}",
                    message=message
                )
            
            return {'status': 'success', 'appointment_id': appointment_id}
            
        except Exception as e:
            logger.error(f"Error sending reminder for appointment {appointment_id}: {str(e)}")
            raise

