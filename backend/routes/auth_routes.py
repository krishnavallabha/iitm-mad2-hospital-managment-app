"""
Authentication routes for login and registration
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import timedelta
from database import db
from models import User, Patient, Doctor
from werkzeug.security import check_password_hash
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Patient registration endpoint
    Only patients can register themselves
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        username = data.get('username').strip()
        email = data.get('email').strip().lower()
        password = data.get('password')
        first_name = data.get('first_name').strip()
        last_name = data.get('last_name').strip()
        phone = data.get('phone', '').strip()
        date_of_birth = data.get('date_of_birth')
        gender = data.get('gender', '').strip()
        address = data.get('address', '').strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user = User(
            username=username,
            email=email,
            role='patient'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Get user.id
        
        # Create patient profile
        patient = Patient(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            phone=phone if phone else None,
            date_of_birth=date_of_birth if date_of_birth else None,
            gender=gender if gender else None,
            address=address if address else None
        )
        
        db.session.add(patient)
        db.session.commit()
        
        # Create access token - identity must be a string
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role, 'username': user.username}
        )
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'profile': patient.to_dict()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint for all user types (Admin, Doctor, Patient)
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data.get('username').strip()
        password = data.get('password')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is inactive. Please contact administrator.'}), 403
        
        # Create access token - identity must be a string
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role, 'username': user.username},
            expires_delta=timedelta(hours=24)
        )
        
        # Create refresh token - identity must be a string
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={'role': user.role, 'username': user.username}
        )
        
        # Get user profile based on role
        profile = None
        if user.role == 'patient' and user.patient_profile:
            profile = user.patient_profile.to_dict()
        elif user.role == 'doctor' and user.doctor_profile:
            profile = user.doctor_profile.to_dict()
        elif user.role == 'admin':
            profile = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': 'admin'
            }
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'profile': profile
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    """
    try:
        user_id = get_jwt_identity()
        # Convert string identity back to int for database query
        user = User.query.get(int(user_id))
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        # Create new access token - identity must be a string
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role, 'username': user.username}
        )
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user information
    """
    try:
        user_id = get_jwt_identity()
        # Convert string identity back to int for database query
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user profile based on role
        profile = None
        if user.role == 'patient' and user.patient_profile:
            profile = user.patient_profile.to_dict()
        elif user.role == 'doctor' and user.doctor_profile:
            profile = user.doctor_profile.to_dict()
        elif user.role == 'admin':
            profile = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': 'admin'
            }
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'profile': profile
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user info: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout endpoint (client should discard tokens)
    In a production system, you might want to blacklist tokens using Redis
    """
    return jsonify({'message': 'Logged out successfully'}), 200

