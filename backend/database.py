"""
Database initialization module
Exports db instance to avoid circular imports
"""
from flask_sqlalchemy import SQLAlchemy

# Create db instance
db = SQLAlchemy()

