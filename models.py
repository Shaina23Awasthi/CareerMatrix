from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    education_level = db.Column(db.String(100), nullable=False)
    interests = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    fees = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    contact_info = db.Column(db.String(100), nullable=True)
    registration_link = db.Column(db.String(255), nullable=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    organization = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    education_required = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False) # e.g. Government, Private
    salary_range = db.Column(db.String(100), nullable=True)
    last_date = db.Column(db.DateTime, nullable=True)
    application_link = db.Column(db.String(255), nullable=True)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
