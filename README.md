# SerenityCare - Hospital Management System

## Problem Statement

Manual appointment scheduling leads to double bookings and scheduling conflicts. Patients struggle to find doctors, book appointments, and access medical history. Administrative overhead increases due to fragmented systems and lack of centralized management.

## Approach

Multi-role web application (Admin, Doctor, Patient) using Flask backend and Vue.js frontend. Real-time appointment booking with conflict prevention and treatment history tracking. Performance optimization through Redis caching and database indexing, with JWT-based security and role-based access control.

## Frameworks and Technologies Used

### Backend
- Flask 3.0.0 - Python web framework
- Flask-SQLAlchemy 3.1.1 - Database ORM
- Flask-JWT-Extended 4.6.0 - Authentication
- Flask-CORS 4.0.0 - Cross-origin resource sharing
- Celery 5.3.4 - Background task queue
- Redis 5.0.1 - Caching and message broker
- SQLite - Database
- Werkzeug 3.0.1 - Password hashing
- ReportLab 4.0.9 - PDF generation
- Twilio 9.0.0 - SMS notifications
- python-dotenv 1.0.0 - Environment variables

### Frontend
- Vue.js 3.4.15 - JavaScript framework
- Vite 5.0.8 - Build tool
- Bootstrap 5.3.3 - CSS framework
- Bootstrap Icons 1.11.3 - Icon library
- Chart.js 4.4.2 - Data visualization
- Axios 1.6.5 - HTTP client

## Running the Application

You need to run multiple services simultaneously. Open 5 separate terminal windows.

### Terminal 1 - Start Redis Server

```bash
.\redis\redis-server.exe
```

Redis server will start and run on port 6379.

### Terminal 2 - Start Celery Worker

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate
celery -A celery_app.celery_app worker --loglevel=info --pool=solo
```

This starts the Celery worker for background tasks.

### Terminal 3 - Start Celery Beat (Scheduler)

```bash
cd backend
.\venv\Scripts\Activate
celery -A celery_app.celery_app beat --loglevel=info
```

This starts Celery Beat for scheduled tasks.

### Terminal 4 - Start Flask Backend

```bash
cd backend
.\venv\Scripts\Activate
pip install -r requirements.txt
python init_db.py
python app.py
```

The Flask server will start on `http://localhost:5000`

Note: Run `python init_db.py` only once to initialize the database. The default admin credentials are:
- Username: `admin`
- Email: `admin@hospital.com`
- Password: `krishna2622`

### Terminal 5 - Start Frontend Development Server

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`

## Default Admin Credentials

- Username: `admin`
- Email: `admin@hospital.com`
- Password: `krishna2622`

Change the admin password after first login.

## Project Structure

```
backend/
├── app.py                 # Flask application
├── models.py              # Database models
├── auth.py                # Authentication decorators
├── database.py            # Database instance
├── celery_app.py          # Celery configuration
├── init_db.py             # Database initialization
├── requirements.txt       # Python dependencies
├── routes/                # API route modules
├── tasks/                 # Celery background tasks
└── utils/                 # Utility functions

frontend/
├── src/
│   ├── components/        # Vue components
│   ├── views/             # Page views
│   ├── services/          # API services
│   └── store/             # State management
├── package.json           # Frontend dependencies
└── vite.config.js         # Vite configuration
```

## Features

- Multi-role authentication (Admin, Doctor, Patient)
- Real-time appointment booking with conflict prevention
- Treatment history tracking
- Doctor availability management
- Patient medical history access
- Background job processing (reminders, reports)
- Redis caching for performance
- PDF export of treatment history
- Responsive PWA support

## API Endpoints

All API endpoints are prefixed with `/api`. Most endpoints require JWT authentication via `Authorization: Bearer <token>` header.

See `backend/API_DOCUMENTATION.md` and `backend/API_ROUTES.md` for complete API documentation.
