# Celery & Redis Setup Guide

## Overview

This guide explains how to set up and run Celery workers, Celery Beat, and Redis for the Hospital Management System backend jobs.

---

## Prerequisites

1. **Redis Server** - Must be installed and running
2. **Python packages** - Install from requirements.txt

---

## Installation

### 1. Install Redis

**Windows:**
- Download from: https://github.com/microsoftarchive/redis/releases
- Or use WSL: `sudo apt-get install redis-server`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Mac
brew install redis
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start Redis Server

**Windows:**
```bash
redis-server
```

**Linux/Mac:**
```bash
redis-server
# Or as a service:
sudo systemctl start redis
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Google Chat Webhook (optional)
GCHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/...

# Twilio SMS (optional)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

---

## Running Celery

### 1. Start Celery Worker

Open a new terminal:

```bash
cd backend
celery -A celery_app worker --loglevel=info --pool=solo
```

For Windows, use `--pool=solo`. For Linux/Mac, you can use:
```bash
celery -A celery_app worker --loglevel=info
```

### 2. Start Celery Beat (Scheduler)

Open another terminal:

```bash
cd backend
celery -A celery_app beat --loglevel=info
```

### 3. Start Flask Application

Open another terminal:

```bash
cd backend
python app.py
```

---

## Scheduled Jobs

### Daily Reminder Job
- **Schedule**: Daily at 8:00 AM
- **Task**: `tasks.reminder_tasks.send_daily_appointment_reminders`
- **Function**: Sends reminders to patients with appointments today
- **Channels**: Email, Google Chat, SMS (if configured)

### Monthly Report Job
- **Schedule**: 1st of every month at 9:00 AM
- **Task**: `tasks.report_tasks.generate_monthly_doctor_reports`
- **Function**: Generates and emails monthly reports to all active doctors
- **Format**: HTML and PDF

---

## User-Triggered Jobs

### CSV Export
- **Trigger**: Patient requests export via API
- **Task**: `tasks.export_tasks.export_patient_treatment_csv`
- **Function**: Exports patient treatment history to CSV
- **Notification**: Email sent when complete

**API Endpoint:**
```bash
POST /api/exports/treatment-history
Authorization: Bearer <patient_token>
```

**Check Status:**
```bash
GET /api/exports/status/<task_id>
Authorization: Bearer <patient_token>
```

---

## Task Queues

Tasks are organized into queues:
- `reminders` - Daily reminder jobs
- `reports` - Monthly report generation
- `default` - CSV exports and other tasks

---

## Monitoring

### Check Celery Status

```bash
celery -A celery_app inspect active
```

### Check Scheduled Tasks

```bash
celery -A celery_app inspect scheduled
```

### View Task Results

Use Redis CLI:
```bash
redis-cli
> KEYS celery-task-meta-*
```

---

## Testing Tasks Manually

### Test Daily Reminder

```python
from tasks.reminder_tasks import send_daily_appointment_reminders
result = send_daily_appointment_reminders.delay()
print(result.get())
```

### Test Monthly Report

```python
from tasks.report_tasks import generate_doctor_report
result = generate_doctor_report.delay(doctor_id=1, month=12, year=2024)
print(result.get())
```

### Test CSV Export

```python
from tasks.export_tasks import export_patient_treatment_csv
result = export_patient_treatment_csv.delay(patient_id=1, user_email='patient@example.com')
print(result.get())
```

---

## Troubleshooting

### Redis Connection Error
- Ensure Redis is running: `redis-cli ping`
- Check REDIS_URL in `.env` file
- Verify Redis is accessible on port 6379

### Celery Worker Not Starting
- Check Redis connection
- Verify all dependencies are installed
- Check for import errors in task files

### Tasks Not Executing
- Verify Celery Beat is running
- Check task schedule in `celery_app.py`
- Review Celery logs for errors

### Email Not Sending
- Verify SMTP credentials in `.env`
- Check email service allows app passwords
- Review notification logs

---

## Production Deployment

### Using Supervisor (Linux)

Create `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A celery_app worker --loglevel=info
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/worker.err.log
stdout_logfile=/var/log/celery/worker.out.log

[program:celery_beat]
command=/path/to/venv/bin/celery -A celery_app beat --loglevel=info
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/beat.err.log
stdout_logfile=/var/log/celery/beat.out.log
```

### Using systemd (Linux)

Create service files for Celery worker and beat.

---

## File Structure

```
backend/
├── celery_app.py              # Celery configuration
├── tasks/
│   ├── __init__.py
│   ├── reminder_tasks.py     # Daily reminder tasks
│   ├── report_tasks.py        # Monthly report tasks
│   └── export_tasks.py       # CSV export tasks
├── utils/
│   ├── notifications.py       # Email/GChat/SMS utilities
│   └── reports.py            # Report generation utilities
├── exports/                   # Generated CSV files
└── reports/                   # Generated PDF reports
```

---

## Quick Start Commands

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
cd backend
celery -A celery_app worker --loglevel=info --pool=solo

# Terminal 3: Celery Beat
cd backend
celery -A celery_app beat --loglevel=info

# Terminal 4: Flask App
cd backend
python app.py
```

---

## Next Steps

1. Configure email/SMS/GChat credentials in `.env`
2. Test daily reminders manually
3. Test monthly reports manually
4. Test CSV export via API
5. Monitor task execution in logs

All backend jobs are now ready to use!

