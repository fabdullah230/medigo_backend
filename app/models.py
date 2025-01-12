# app/models.py
from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), unique=True)
    auth_number = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    identifying_document_id = db.Column(db.String(50))
    bkash_number = db.Column(db.String(20))
    precondition_keywords = db.Column(db.JSON)
    address = db.Column(db.Text)
    is_primary_user = db.Column(db.Boolean, default=True)
    primary_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dependents = db.relationship('User', backref=db.backref('primary_user', remote_side=[id]))

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), unique=True)
    specializations = db.Column(db.JSON)
    hospital_affiliations = db.Column(db.JSON)
    degrees = db.Column(db.JSON)
    chambers = db.relationship('Chamber', secondary='doctor_chamber', backref='doctors')

doctor_chamber = db.Table('doctor_chamber',
    db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id')),
    db.Column('chamber_id', db.Integer, db.ForeignKey('chamber.id'))
)

class Chamber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Text, nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    operators = db.relationship('User', secondary='chamber_operator')

chamber_operator = db.Table('chamber_operator',
    db.Column('chamber_id', db.Integer, db.ForeignKey('chamber.id')),
    db.Column('operator_id', db.Integer, db.ForeignKey('user.id'))
)

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chamber_id = db.Column(db.Integer, db.ForeignKey('chamber.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    booking_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    patient_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    visit_document_ids = db.Column(db.JSON)
    booking_remarks = db.Column(db.Text)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    appointment_time = db.Column(db.DateTime, nullable=False)
    visit_end_time = db.Column(db.DateTime)
    visit_cost = db.Column(db.Float)
    visit_status = db.Column(db.String(20))
    cancel_reason = db.Column(db.Text)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chamber_id = db.Column(db.Integer, db.ForeignKey('chamber.id'))
    time_slots = db.Column(db.JSON)  # Store available time slots as JSON

# Add to app/models.py
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visit.id'))
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20))
    bkash_number = db.Column(db.String(20))
    transaction_id = db.Column(db.String(50))
    status = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)