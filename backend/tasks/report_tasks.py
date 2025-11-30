"""
Monthly report generation tasks for doctors
"""
from celery_app import celery_app

from database import db
from models import Doctor, Appointment, Treatment, Department
from datetime import date, datetime, timedelta
from utils.reports import generate_doctor_report_html, generate_doctor_report_pdf
from utils.notifications import send_email_notification
import logging
from calendar import monthrange

# Create app instance for Celery
@celery_app.task(name='tasks.report_tasks.generate_monthly_doctor_reports', bind=True)
def generate_monthly_doctor_reports(self):
    """
    Generate and send monthly reports for all active doctors
    Runs on the 1st of every month at 9:00 AM
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        try:
            # Get previous month
            today = date.today()
            if today.month == 1:
                report_month = 12
                report_year = today.year - 1
            else:
                report_month = today.month - 1
                report_year = today.year
            
            # Get all active doctors
            doctors = Doctor.query.filter_by(is_active=True).all()
            
            logger.info(f"Generating monthly reports for {len(doctors)} doctors for {report_month}/{report_year}")
            
            reports_generated = 0
            reports_failed = 0
            
            for doctor in doctors:
                try:
                    # Generate report
                    report_data = generate_doctor_monthly_report_data(doctor.id, report_month, report_year)
                    
                    if not report_data:
                        logger.warning(f"No data found for doctor {doctor.id} in {report_month}/{report_year}")
                        continue
                    
                    # Generate HTML report
                    html_report = generate_doctor_report_html(report_data)
                    
                    # Generate PDF report (optional)
                    pdf_path = None
                    try:
                        pdf_path = generate_doctor_report_pdf(report_data, doctor.id, report_month, report_year)
                    except Exception as e:
                        logger.warning(f"PDF generation failed for doctor {doctor.id}: {str(e)}")
                    
                    # Send email with report
                    if doctor.user and doctor.user.email:
                        email_sent = send_doctor_report_email(
                            doctor=doctor,
                            report_data=report_data,
                            html_report=html_report,
                            pdf_path=pdf_path,
                            month=report_month,
                            year=report_year
                        )
                        
                        if email_sent:
                            reports_generated += 1
                        else:
                            reports_failed += 1
                    else:
                        logger.warning(f"No email found for doctor {doctor.id}")
                        reports_failed += 1
                    
                except Exception as e:
                    logger.error(f"Error generating report for doctor {doctor.id}: {str(e)}")
                    reports_failed += 1
                    continue
            
            result = {
                'status': 'completed',
                'month': report_month,
                'year': report_year,
                'total_doctors': len(doctors),
                'reports_generated': reports_generated,
                'reports_failed': reports_failed
            }
            
            logger.info(f"Monthly reports generation completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in monthly report task: {str(e)}")
            raise

@celery_app.task(name='tasks.report_tasks.generate_doctor_report', bind=True)
def generate_doctor_report(self, doctor_id, month=None, year=None):
    """
    Generate report for a specific doctor
    Can be triggered manually
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        try:
            doctor = Doctor.query.get(doctor_id)
            
            if not doctor:
                return {'status': 'error', 'message': 'Doctor not found'}
            
            # Use current month if not specified
            if not month or not year:
                today = date.today()
                month = today.month
                year = today.year
            
            report_data = generate_doctor_monthly_report_data(doctor_id, month, year)
            
            if not report_data:
                return {'status': 'error', 'message': 'No data found for the specified period'}
            
            html_report = generate_doctor_report_html(report_data)
            
            return {
                'status': 'success',
                'doctor_id': doctor_id,
                'month': month,
                'year': year,
                'html_report': html_report,
                'report_data': report_data
            }
            
        except Exception as e:
            logger.error(f"Error generating report for doctor {doctor_id}: {str(e)}")
            raise

def generate_doctor_monthly_report_data(doctor_id, month, year):
    """
    Generate report data for a doctor for a specific month
    """
    try:
        doctor = Doctor.query.get(doctor_id)
        
        if not doctor:
            return None
        
        # Calculate date range
        start_date = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        
        # Get appointments for the month
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        
        # Get treatments
        treatments = Treatment.query.join(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).all()
        
        # Calculate statistics
        total_appointments = len(appointments)
        completed = len([a for a in appointments if a.status == 'Completed'])
        cancelled = len([a for a in appointments if a.status == 'Cancelled'])
        booked = len([a for a in appointments if a.status == 'Booked'])
        
        # Get unique patients
        patient_ids = list(set([a.patient_id for a in appointments]))
        unique_patients = len(patient_ids)
        
        # Get diagnosis summary
        diagnosis_summary = {}
        for treatment in treatments:
            if treatment.diagnosis:
                diagnosis = treatment.diagnosis[:50]  # First 50 chars
                diagnosis_summary[diagnosis] = diagnosis_summary.get(diagnosis, 0) + 1
        
        return {
            'doctor': doctor.to_dict(),
            'period': {
                'month': month,
                'year': year,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'statistics': {
                'total_appointments': total_appointments,
                'completed': completed,
                'cancelled': cancelled,
                'booked': booked,
                'unique_patients': unique_patients,
                'treatments_provided': len(treatments)
            },
            'appointments': [a.to_dict() for a in appointments],
            'treatments': [t.to_dict() for t in treatments],
            'diagnosis_summary': diagnosis_summary
        }
        
    except Exception as e:
        logger.error(f"Error generating report data: {str(e)}")
        return None

def send_doctor_report_email(doctor, report_data, html_report, pdf_path, month, year):
    """
    Send monthly report email to doctor
    """
    try:
        if not doctor.user or not doctor.user.email:
            return False
        
        month_name = datetime(year, month, 1).strftime('%B %Y')
        
        subject = f"Monthly Activity Report - {month_name}"
        
        # Create email body
        email_body = f"""
Dear Dr. {doctor.first_name} {doctor.last_name},

Please find attached your monthly activity report for {month_name}.

Summary:
- Total Appointments: {report_data['statistics']['total_appointments']}
- Completed: {report_data['statistics']['completed']}
- Cancelled: {report_data['statistics']['cancelled']}
- Unique Patients: {report_data['statistics']['unique_patients']}
- Treatments Provided: {report_data['statistics']['treatments_provided']}

The detailed report is attached as HTML and PDF.

Thank you,
Hospital Management System
"""
        
        # Send email with HTML report
        return send_email_notification(
            to_email=doctor.user.email,
            subject=subject,
            message=email_body,
            html_message=html_report
        )
        
    except Exception as e:
        logger.error(f"Error sending report email: {str(e)}")
        return False

