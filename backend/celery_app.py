"""
Celery application configuration
"""
from celery import Celery
from celery.schedules import crontab
import os

# Redis configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery instance
celery_app = Celery(
    'hospital_management',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['tasks.reminder_tasks', 'tasks.report_tasks', 'tasks.export_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'daily-appointment-reminders': {
        'task': 'tasks.reminder_tasks.send_daily_appointment_reminders',
        'schedule': crontab(hour=8, minute=0),  # Run daily at 8:00 AM
        'options': {'queue': 'reminders'}
    },
    'monthly-doctor-reports': {
        'task': 'tasks.report_tasks.generate_monthly_doctor_reports',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # Run on 1st of every month at 9:00 AM
        'options': {'queue': 'reports'}
    },
}

if __name__ == '__main__':
    celery_app.start()

