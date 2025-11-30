"""
Authentication utilities and decorators
"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import User

def role_required(*allowed_roles):
    """
    Decorator to require specific role(s) for access
    Usage: @role_required('admin') or @role_required('admin', 'doctor')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip authentication for OPTIONS requests (CORS preflight)
            # Flask-CORS will handle the OPTIONS response
            if request.method == 'OPTIONS':
                response = jsonify({})
                return response
            
            # Verify JWT token is present
            verify_jwt_in_request()
            
            # Get current user identity
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({'error': 'Invalid token'}), 401
            
            # Get user from database - convert string identity to int
            try:
                user = User.query.get(int(user_id))
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid user ID in token'}), 401
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Check if user role is allowed
            if user.role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_roles': list(allowed_roles),
                    'user_role': user.role
                }), 403
            
            # Add user to kwargs for use in route
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """
    Helper function to get current authenticated user
    Returns User object or None
    """
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            # Convert string identity to int for database query
            try:
                return User.query.get(int(user_id))
            except (ValueError, TypeError):
                return None
    except:
        pass
    return None

def admin_required(f):
    """Decorator for admin-only routes"""
    return role_required('admin')(f)

def doctor_required(f):
    """Decorator for doctor-only routes"""
    return role_required('doctor')(f)

def patient_required(f):
    """Decorator for patient-only routes"""
    return role_required('patient')(f)

def admin_or_doctor_required(f):
    """Decorator for admin or doctor routes"""
    return role_required('admin', 'doctor')(f)

