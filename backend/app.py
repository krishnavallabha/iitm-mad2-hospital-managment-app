from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from database import db

# Initialize CORS
cors = CORS()
jwt = JWTManager()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'hospital.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or app.config['SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Set to timedelta(hours=24) for production
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = False  # Set to timedelta(days=30) for production
    # Explicitly tell JWT where to look for tokens
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    # CORS Configuration - Allow Authorization header
    # For development, allow all origins. In production, specify exact origins.
    cors.init_app(app, 
        resources={
            r"/api/*": {
                "origins": "*",  # Allow all origins in development
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "expose_headers": ["Content-Type", "Authorization"],
                "supports_credentials": False,
                "max_age": 3600
            }
        }
    )
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    
    # Import models (must be after db initialization)
    from models import User, Doctor, Patient, Department, Appointment, Treatment
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.admin_routes import admin_bp
    from routes.doctor_routes import doctor_bp
    from routes.patient_routes import patient_bp
    from routes.history_routes import history_bp
    from routes.export_routes import export_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(export_bp)
    
    # Error handlers for JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': f'Invalid token: {str(error)}'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        # Debug: Log what headers we received
        auth_header = request.headers.get('Authorization', 'NOT FOUND')
        print(f"\n[DEBUG] Authorization header received: {auth_header}")
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] Request path: {request.path}")
        print(f"[DEBUG] All headers: {dict(request.headers)}")
        return jsonify({
            'error': 'Authorization token is missing',
            'debug': {
                'auth_header_present': 'Authorization' in request.headers,
                'auth_header_value': auth_header[:50] if auth_header != 'NOT FOUND' else 'NOT FOUND',
                'request_method': request.method,
                'request_path': request.path
            }
        }), 401
    
    return app

# Create app instance
app = create_app()

# Create database tables
def create_tables():
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=5000)

