"""
Routes for triggering and managing CSV exports
"""
from flask import Blueprint, request, jsonify, send_file
from auth import patient_required, admin_required
from database import db
from models import Patient
from tasks.export_tasks import export_patient_treatment_pdf, export_patient_treatment_csv, generate_pdf_export, generate_csv_export
from celery.result import AsyncResult
from celery_app import celery_app
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

export_bp = Blueprint('export', __name__, url_prefix='/api/exports')

def is_celery_available():
    """Check if Celery is available and working"""
    try:
        # Try to inspect active tasks - if this works, Celery is available
        inspector = celery_app.control.inspect()
        if inspector:
            inspector.active()
            return True
        return False
    except Exception as e:
        logger.debug(f"Celery not available: {str(e)}")
        return False

@export_bp.route('/treatment-history', methods=['POST'])
@patient_required
def trigger_treatment_export(current_user):
    """
    Patient: Trigger CSV or PDF export of treatment history
    Body: { "format": "csv" | "pdf" } (default: "pdf")
    Returns task ID for tracking or direct download URL
    """
    try:
        patient = current_user.patient_profile
        
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        data = request.get_json() or {}
        export_format = data.get('format', 'pdf').lower()
        
        # For PDF, use synchronous export (no Celery required)
        if export_format == 'pdf':
            try:
                result = generate_pdf_export(patient_id=patient.id, user_email=current_user.email)
                return jsonify({
                    'message': 'PDF export completed successfully',
                    'status': 'completed',
                    'format': export_format,
                    'result': result
                }), 200
            except Exception as e:
                logger.error(f"Error generating PDF export: {str(e)}")
                return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500
        
        # For CSV, try Celery if available, otherwise use synchronous
        elif export_format == 'csv':
            if is_celery_available():
                try:
                    task = export_patient_treatment_csv.delay(
                        patient_id=patient.id,
                        user_email=current_user.email
                    )
                    return jsonify({
                        'message': f'{export_format.upper()} export job started',
                        'task_id': task.id,
                        'format': export_format,
                        'status': 'processing',
                        'check_status_url': f'/api/exports/status/{task.id}'
                    }), 202
                except Exception as e:
                    logger.warning(f"Celery task failed, falling back to synchronous: {str(e)}")
            
            # Fallback to synchronous CSV export
            try:
                result = generate_csv_export(patient_id=patient.id, user_email=current_user.email)
                return jsonify({
                    'message': 'CSV export completed successfully',
                    'status': 'completed',
                    'format': export_format,
                    'result': result
                }), 200
            except Exception as e:
                logger.error(f"Error generating CSV export: {str(e)}")
                return jsonify({'error': f'Failed to generate CSV: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Invalid format. Use "pdf" or "csv"'}), 400
        
    except Exception as e:
        logger.error(f"Error triggering export: {str(e)}")
        return jsonify({'error': f'Failed to start export: {str(e)}'}), 500

@export_bp.route('/status/<task_id>', methods=['GET'])
@patient_required
def get_export_status(current_user, task_id):
    """
    Check status of export job
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'status': 'pending',
                'message': 'Job is waiting to be processed'
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'status': 'processing',
                'message': 'Job is being processed',
                'progress': task_result.info.get('progress', 0) if isinstance(task_result.info, dict) else None
            }
        elif task_result.state == 'SUCCESS':
            result = task_result.result
            response = {
                'task_id': task_id,
                'status': 'completed',
                'message': 'Export completed successfully',
                'result': result
            }
        elif task_result.state == 'FAILURE':
            response = {
                'task_id': task_id,
                'status': 'failed',
                'message': 'Export job failed',
                'error': str(task_result.info)
            }
        else:
            response = {
                'task_id': task_id,
                'status': task_result.state.lower(),
                'message': f'Job state: {task_result.state}'
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error checking export status: {str(e)}")
        return jsonify({'error': f'Failed to check status: {str(e)}'}), 500

@export_bp.route('/download/<filename>', methods=['GET'])
@patient_required
def download_export(current_user, filename):
    """
    Download exported CSV file
    """
    try:
        # Security: Verify filename belongs to current user
        if not filename.startswith(f'patient_{current_user.patient_profile.id}_'):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
        filepath = os.path.join(exports_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Determine mimetype based on file extension
        if filename.endswith('.csv'):
            mimetype = 'text/csv'
        else:
            mimetype = 'application/pdf'
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        logger.error(f"Error downloading export: {str(e)}")
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

@export_bp.route('/my-exports', methods=['GET'])
@patient_required
def list_my_exports(current_user):
    """
    List all exports for current patient
    """
    try:
        patient = current_user.patient_profile
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
        
        if not os.path.exists(exports_dir):
            return jsonify({'exports': [], 'count': 0}), 200
        
        # Get all files for this patient
        prefix = f'patient_{patient.id}_'
        exports = []
        
        for filename in os.listdir(exports_dir):
            if filename.startswith(prefix) and (filename.endswith('.pdf') or filename.endswith('.csv')):
                filepath = os.path.join(exports_dir, filename)
                file_stat = os.stat(filepath)
                
                exports.append({
                    'filename': filename,
                    'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    'size': file_stat.st_size,
                    'download_url': f'/api/exports/download/{filename}'
                })
        
        # Sort by creation time (newest first)
        exports.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'exports': exports,
            'count': len(exports)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing exports: {str(e)}")
        return jsonify({'error': f'Failed to list exports: {str(e)}'}), 500

