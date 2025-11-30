"""
PDF and CSV export tasks for patient treatment history
"""
from celery_app import celery_app

from database import db
from models import Patient, Appointment, Treatment, Doctor
from datetime import datetime
import os
import csv
import logging
from utils.notifications import send_email_notification
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

logger = logging.getLogger(__name__)

def generate_pdf_export(patient_id, user_email=None):
    """
    Synchronous function to export patient treatment history to PDF
    Can be called directly without Celery
    """
    try:
        patient = Patient.query.get(patient_id)
        
        if not patient:
            raise ValueError('Patient not found')
        
        # Get all appointments with treatments
        appointments = Appointment.query.filter_by(
            patient_id=patient_id
        ).order_by(
            Appointment.appointment_date.desc()
        ).all()
        
        # Create exports directory
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"patient_{patient_id}_treatment_history_{timestamp}.pdf"
        filepath = os.path.join(exports_dir, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = styles['Heading1']
        elements.append(Paragraph(f"Medical History Report", title_style))
        elements.append(Spacer(1, 12))
        
        # Patient Info
        elements.append(Paragraph(f"Patient: {patient.first_name} {patient.last_name}", styles['Normal']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 24))
        
        # Table Data
        data = [['Date', 'Doctor', 'Diagnosis', 'Treatment/Meds']]
        
        for appointment in appointments:
            treatment = appointment.treatment
            doctor = appointment.doctor
            
            date_str = appointment.appointment_date.strftime('%Y-%m-%d') if appointment.appointment_date else 'N/A'
            doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else 'N/A'
            
            diagnosis = 'N/A'
            meds = 'N/A'
            
            if treatment:
                diagnosis = treatment.diagnosis or 'N/A'
                meds_list = []
                if treatment.prescription:
                    meds_list.append(f"Rx: {treatment.prescription}")
                if treatment.medicines:
                    meds_list.append(f"Meds: {treatment.medicines}")
                if treatment.tests_done:
                    meds_list.append(f"Tests: {treatment.tests_done}")
                
                if meds_list:
                    meds = "\n".join(meds_list)
                elif treatment.notes:
                    meds = treatment.notes
            
            data.append([date_str, doctor_name, diagnosis, meds])
        
        # Table Style
        table = Table(data, colWidths=[80, 100, 120, 240])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        # Send notification email if email provided
        if user_email:
            try:
                send_export_completion_email(user_email, filename, filepath, len(appointments))
            except Exception as e:
                logger.error(f"Failed to send export completion email: {str(e)}")
        
        result = {
            'status': 'success',
            'patient_id': patient_id,
            'filename': filename,
            'filepath': filepath,
            'total_records': len(appointments),
            'download_url': f'/api/exports/download/{filename}'
        }
        
        logger.info(f"PDF export completed for patient {patient_id}: {filename}")
        return result
        
    except Exception as e:
        logger.error(f"Error exporting PDF for patient {patient_id}: {str(e)}")
        raise

def generate_csv_export(patient_id, user_email=None):
    """
    Synchronous function to export patient treatment history to CSV
    Can be called directly without Celery
    """
    try:
        patient = Patient.query.get(patient_id)
        
        if not patient:
            raise ValueError('Patient not found')
        
        # Get all appointments with treatments
        appointments = Appointment.query.filter_by(
            patient_id=patient_id
        ).order_by(
            Appointment.appointment_date.desc()
        ).all()
        
        # Create exports directory
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"patient_{patient_id}_treatment_history_{timestamp}.csv"
        filepath = os.path.join(exports_dir, filename)
        
        # Create CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'User ID',
                'Username',
                'Consulting Doctor',
                'Appointment Date',
                'Appointment Time',
                'Diagnosis',
                'Treatment',
                'Prescription',
                'Medicines',
                'Tests Done',
                'Doctor Notes',
                'Next Visit Suggested',
                'Follow-up Date',
                'Follow-up Notes'
            ])
            
            # Write data rows
            for appointment in appointments:
                treatment = appointment.treatment
                doctor = appointment.doctor
                user = patient.user
                
                user_id = user.id if user else 'N/A'
                username = user.username if user else 'N/A'
                doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else 'N/A'
                appointment_date = appointment.appointment_date.strftime('%Y-%m-%d') if appointment.appointment_date else 'N/A'
                appointment_time = appointment.appointment_time.strftime('%H:%M') if appointment.appointment_time else 'N/A'
                
                diagnosis = treatment.diagnosis if treatment and treatment.diagnosis else 'N/A'
                treatment_text = treatment.notes if treatment and treatment.notes else 'N/A'
                prescription = treatment.prescription if treatment and treatment.prescription else 'N/A'
                medicines = treatment.medicines if treatment and treatment.medicines else 'N/A'
                tests_done = treatment.tests_done if treatment and treatment.tests_done else 'N/A'
                doctor_notes = treatment.notes if treatment and treatment.notes else 'N/A'
                next_visit = treatment.follow_up_date.strftime('%Y-%m-%d') if treatment and treatment.follow_up_date else 'N/A'
                follow_up_date = treatment.follow_up_date.strftime('%Y-%m-%d') if treatment and treatment.follow_up_date else 'N/A'
                follow_up_notes = treatment.follow_up_notes if treatment and treatment.follow_up_notes else 'N/A'
                
                writer.writerow([
                    user_id,
                    username,
                    doctor_name,
                    appointment_date,
                    appointment_time,
                    diagnosis,
                    treatment_text,
                    prescription,
                    medicines,
                    tests_done,
                    doctor_notes,
                    next_visit,
                    follow_up_date,
                    follow_up_notes
                ])
        
        # Send notification email if email provided
        if user_email:
            try:
                send_export_completion_email(user_email, filename, filepath, len(appointments), 'CSV')
            except Exception as e:
                logger.error(f"Failed to send export completion email: {str(e)}")
        
        result = {
            'status': 'success',
            'patient_id': patient_id,
            'filename': filename,
            'filepath': filepath,
            'total_records': len(appointments),
            'download_url': f'/api/exports/download/{filename}'
        }
        
        logger.info(f"CSV export completed for patient {patient_id}: {filename}")
        return result
        
    except Exception as e:
        logger.error(f"Error exporting CSV for patient {patient_id}: {str(e)}")
        raise

# Create app instance for Celery
@celery_app.task(name='tasks.export_tasks.export_patient_treatment_pdf', bind=True)
def export_patient_treatment_pdf(self, patient_id, user_email=None):
    """
    Export patient treatment history to PDF (Celery task wrapper)
    User-triggered async job
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        try:
            result = generate_pdf_export(patient_id, user_email)
            result['task_id'] = self.request.id
            return result
        except Exception as e:
            logger.error(f"Error exporting PDF for patient {patient_id}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'task_id': self.request.id
            }

@celery_app.task(name='tasks.export_tasks.export_patient_treatment_csv', bind=True)
def export_patient_treatment_csv(self, patient_id, user_email=None):
    """
    Export patient treatment history to CSV (Celery task wrapper)
    User-triggered async job
    Format: user_id, username, consulting doctor, appointment date, diagnosis, treatment, next visit
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        try:
            result = generate_csv_export(patient_id, user_email)
            result['task_id'] = self.request.id
            return result
        except Exception as e:
            logger.error(f"Error exporting CSV for patient {patient_id}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'task_id': self.request.id
            }

def send_export_completion_email(user_email, filename, filepath, record_count, file_type='PDF'):
    """
    Send email notification when export is complete
    """
    try:
        subject = f"Your Medical History Report is Ready ({file_type})"
        
        message = f"""
Dear User,

Your medical history report has been generated successfully.

File: {filename}
Format: {file_type}
Records: {record_count}

You can download the file from your dashboard or use the download link provided.

Thank you,
Hospital Management System
"""
        
        send_email_notification(
            to_email=user_email,
            subject=subject,
            message=message
        )
        
        logger.info(f"Export completion email sent to {user_email}")
        
    except Exception as e:
        logger.error(f"Error sending export completion email: {str(e)}")

