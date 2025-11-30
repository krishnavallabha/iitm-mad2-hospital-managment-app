# Hospital Management System - API Documentation

## Authentication Endpoints

### Base URL
All API endpoints are prefixed with `/api`

### Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Auth Endpoints

### 1. Patient Registration
**POST** `/api/auth/register`

Register a new patient account.

**Request Body:**
```json
{
  "username": "string (required)",
  "email": "string (required)",
  "password": "string (required, min 6 chars)",
  "first_name": "string (required)",
  "last_name": "string (required)",
  "phone": "string (optional)",
  "date_of_birth": "YYYY-MM-DD (optional)",
  "gender": "string (optional)",
  "address": "string (optional)"
}
```

**Response (201):**
```json
{
  "message": "Registration successful",
  "access_token": "jwt_token",
  "user": {
    "id": 1,
    "username": "testpatient",
    "email": "test@example.com",
    "role": "patient",
    "profile": { ... }
  }
}
```

**Error Responses:**
- `400` - Validation error (missing fields, invalid email, etc.)
- `400` - Username or email already exists
- `500` - Server error

---

### 2. Login
**POST** `/api/auth/login`

Login for Admin, Doctor, or Patient.

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "jwt_token",
  "refresh_token": "jwt_refresh_token",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@hospital.com",
    "role": "admin|doctor|patient",
    "profile": { ... }
  }
}
```

**Error Responses:**
- `400` - Missing username or password
- `401` - Invalid credentials
- `403` - Account inactive

---

### 3. Get Current User
**GET** `/api/auth/me`

Get information about the currently authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@hospital.com",
    "role": "admin",
    "is_active": true,
    "profile": { ... }
  }
}
```

---

### 4. Refresh Token
**POST** `/api/auth/refresh`

Get a new access token using a refresh token.

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response (200):**
```json
{
  "access_token": "new_jwt_token"
}
```

---

### 5. Logout
**POST** `/api/auth/logout`

Logout (client should discard tokens).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

## Dashboard Endpoints

### 1. Get Dashboard Redirect
**GET** `/api/dashboard/redirect`

Returns the appropriate dashboard URL based on user role. Use this after login to redirect users.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "role": "admin|doctor|patient",
  "dashboard_url": "/api/dashboard/admin",
  "redirect_to": "/api/dashboard/admin"
}
```

---

### 2. Admin Dashboard
**GET** `/api/dashboard/admin`

Get admin dashboard with statistics and overview.

**Access:** Admin only

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "role": "admin",
  "dashboard": "admin",
  "statistics": {
    "total_doctors": 10,
    "total_patients": 50,
    "total_appointments": 200,
    "upcoming_appointments": 15,
    "completed_appointments": 185
  },
  "recent_appointments": [ ... ],
  "user": { ... }
}
```

---

### 3. Doctor Dashboard
**GET** `/api/dashboard/doctor`

Get doctor dashboard with appointments and patients.

**Access:** Doctor only

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "role": "doctor",
  "dashboard": "doctor",
  "doctor": { ... },
  "statistics": {
    "appointments_today": 5,
    "completed_today": 3,
    "upcoming_this_week": 12,
    "total_patients": 25
  },
  "today_appointments": [ ... ],
  "upcoming_appointments": [ ... ],
  "assigned_patients": [ ... ],
  "user": { ... }
}
```

---

### 4. Patient Dashboard
**GET** `/api/dashboard/patient`

Get patient dashboard with departments, doctors, and appointments.

**Access:** Patient only

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "role": "patient",
  "dashboard": "patient",
  "patient": { ... },
  "departments": [ ... ],
  "upcoming_appointments": [ ... ],
  "past_appointments": [ ... ],
  "statistics": {
    "upcoming_count": 2,
    "past_count": 5,
    "total_departments": 8
  },
  "user": { ... }
}
```

---

## Role-Based Access Control

### Decorators

The following decorators are available for protecting routes:

- `@admin_required` - Only admin can access
- `@doctor_required` - Only doctor can access
- `@patient_required` - Only patient can access
- `@role_required('admin', 'doctor')` - Multiple roles allowed
- `@jwt_required()` - Any authenticated user

### Example Usage

```python
from auth import admin_required, doctor_required, patient_required
from flask_jwt_extended import jwt_required

@admin_required
def admin_only_route(current_user):
    # current_user is automatically injected
    pass

@doctor_required
def doctor_only_route(current_user):
    pass

@jwt_required()
def any_authenticated_user():
    # Use get_jwt_identity() to get user_id
    pass
```

---

## Error Responses

All endpoints may return the following error responses:

- `400` - Bad Request (validation errors, missing fields)
- `401` - Unauthorized (invalid/missing token, invalid credentials)
- `403` - Forbidden (insufficient permissions, inactive account)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

Error response format:
```json
{
  "error": "Error message description"
}
```

---

## Frontend Integration

### Login Flow

1. User submits login form
2. POST to `/api/auth/login`
3. Store `access_token` and `refresh_token` in localStorage/sessionStorage
4. Call `/api/dashboard/redirect` to get dashboard URL
5. Redirect user to appropriate dashboard based on role

### Registration Flow (Patients Only)

1. Patient submits registration form
2. POST to `/api/auth/register`
3. Store `access_token` in localStorage/sessionStorage
4. Redirect to patient dashboard

### Making Authenticated Requests

Include the token in all API requests:
```javascript
fetch('/api/dashboard/admin', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

### Token Refresh

When access token expires:
1. POST to `/api/auth/refresh` with refresh token
2. Get new access token
3. Update stored token

---

## Default Credentials

After running `init_db.py`, the default admin credentials are:

- **Username:** `admin`
- **Email:** `admin@hospital.com`
- **Password:** `admin123`

[IMPORTANT] **Change this password after first login!**

---

## Testing

Use the provided `test_auth.py` script to test authentication:

```bash
# Start Flask server
python app.py

# In another terminal, run tests
python test_auth.py
```

