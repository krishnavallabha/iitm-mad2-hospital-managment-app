# Hospital Management System - Complete API Routes

## Base URL
All API endpoints are prefixed with `/api`

## Authentication
Include JWT token in Authorization header: `Authorization: Bearer <access_token>`

---

## Authentication Routes (`/api/auth`)

- `POST /api/auth/register` - Patient registration
- `POST /api/auth/login` - Login (all roles)
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Logout

---

## Admin Routes (`/api/admin`)

### Dashboard
- `GET /api/admin/dashboard` - Admin dashboard with statistics

### Doctor Management
- `GET /api/admin/doctors` - Get all doctors (search, filter by specialization, active status)
- `POST /api/admin/doctors` - Add new doctor
- `GET /api/admin/doctors/<id>` - Get doctor details
- `PUT /api/admin/doctors/<id>` - Update doctor
- `DELETE /api/admin/doctors/<id>` - Blacklist doctor (soft delete)

### Patient Management
- `GET /api/admin/patients` - Get all patients (search by name, ID, contact)
- `GET /api/admin/patients/<id>` - Get patient details with history
- `PUT /api/admin/patients/<id>` - Update patient
- `DELETE /api/admin/patients/<id>` - Blacklist patient (soft delete)

### Appointment Management
- `GET /api/admin/appointments` - Get all appointments (filter by status, date, doctor, patient)
- `GET /api/admin/appointments/<id>` - Get appointment details
- `PUT /api/admin/appointments/<id>` - Update appointment
- `DELETE /api/admin/appointments/<id>` - Cancel appointment

### Department Management
- `GET /api/admin/departments` - Get all departments
- `POST /api/admin/departments` - Add new department

---

## Doctor Routes (`/api/doctor`)

### Dashboard
- `GET /api/doctor/dashboard` - Doctor dashboard with appointments and statistics

### Appointments
- `GET /api/doctor/appointments` - Get doctor's appointments (filter by status, date)
- `GET /api/doctor/appointments/<id>` - Get appointment details
- `PUT /api/doctor/appointments/<id>/complete` - Mark appointment as completed
- `PUT /api/doctor/appointments/<id>/cancel` - Cancel appointment

### Treatments
- `POST /api/doctor/appointments/<id>/treatment` - Add treatment record
- `PUT /api/doctor/appointments/<id>/treatment` - Update treatment record

### Patient History
- `GET /api/doctor/patients` - Get assigned patients
- `GET /api/doctor/patients/<id>` - Get full patient medical history

### Availability
- `GET /api/doctor/availability` - Get availability for next 7 days
- `POST /api/doctor/availability` - Set availability slots (array of slots)
- `PUT /api/doctor/availability/<id>` - Update availability slot
- `DELETE /api/doctor/availability/<id>` - Delete availability slot

---

## 👤 Patient Routes (`/api/patient`)

### Dashboard
- `GET /api/patient/dashboard` - Patient dashboard with departments, doctors, appointments

### Profile
- `GET /api/patient/profile` - Get patient profile
- `PUT /api/patient/profile` - Update patient profile

### Doctors Search
- `GET /api/patient/doctors` - Search doctors (by name, specialization, availability date)
- `GET /api/patient/doctors/<id>` - Get doctor details with availability

### Appointments
- `GET /api/patient/appointments` - Get patient's appointments (filter by status, upcoming_only)
- `POST /api/patient/appointments` - Book new appointment
- `PUT /api/patient/appointments/<id>` - Reschedule appointment
- `DELETE /api/patient/appointments/<id>` - Cancel appointment
- `GET /api/patient/appointments/<id>` - Get appointment details with treatment

### Departments
- `GET /api/patient/departments` - Get all departments with doctor counts

---

## 📊 Dashboard Routes (`/api/dashboard`)

- `GET /api/dashboard/redirect` - Get dashboard URL based on role
- `GET /api/dashboard/admin` - Admin dashboard (same as `/api/admin/dashboard`)
- `GET /api/dashboard/doctor` - Doctor dashboard (same as `/api/doctor/dashboard`)
- `GET /api/dashboard/patient` - Patient dashboard (same as `/api/patient/dashboard`)

---

## Key Features Implemented

### Admin Features
- Dashboard with statistics (doctors, patients, appointments)
- Add/Update/Delete doctors
- Search doctors by name/specialization
- Search patients by name/ID/contact
- View/manage all appointments
- Blacklist doctors & patients
- Department management

### Doctor Features
- Dashboard with upcoming appointments
- View assigned patients
- Mark appointments as completed/cancelled
- Add/Update treatment records (diagnosis, prescription, notes)
- Update availability for next 7 days
- Access full patient medical history

### Patient Features
- Register, login, update profile
- Search doctors by specialization/name
- View doctor availability (next 7 days)
- Book appointments (with conflict checking)
- Reschedule appointments
- Cancel appointments
- View upcoming appointments
- View past appointments with treatment history

### Additional Features
- Appointment conflict prevention (same doctor, same time)
- Availability-based appointment booking
- Soft delete (blacklist) for doctors and patients
- Comprehensive search functionality
- Treatment history tracking
- Follow-up date tracking
- Medical history storage

---

## Request/Response Examples

### Book Appointment (Patient)
```json
POST /api/patient/appointments
{
  "doctor_id": 1,
  "appointment_date": "2024-01-15",
  "appointment_time": "10:00",
  "reason": "Regular checkup"
}
```

### Add Treatment (Doctor)
```json
POST /api/doctor/appointments/1/treatment
{
  "diagnosis": "Common cold",
  "prescription": "Rest and fluids",
  "notes": "Patient should rest for 2-3 days",
  "follow_up_date": "2024-01-20",
  "follow_up_notes": "Return if symptoms persist"
}
```

### Set Availability (Doctor)
```json
POST /api/doctor/availability
[
  {
    "date": "2024-01-15",
    "start_time": "09:00",
    "end_time": "17:00",
    "is_available": true
  },
  {
    "date": "2024-01-16",
    "start_time": "09:00",
    "end_time": "13:00",
    "is_available": true
  }
]
```

---

## Error Responses

All endpoints return standard error responses:
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

Error format:
```json
{
  "error": "Error message description"
}
```

