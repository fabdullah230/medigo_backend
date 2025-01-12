# app/routes/doctors.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Doctor, db
from app.schemas import DoctorSchema
from sqlalchemy import or_

bp = Blueprint('doctors', __name__, url_prefix='/doctors')
doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many=True)


@bp.route('', methods=['GET'])
def get_doctors():
    # Get query parameters for filtering
    specialization = request.args.get('specialization')
    location = request.args.get('location')
    name = request.args.get('name')
    hospital = request.args.get('hospital')

    query = Doctor.query

    # Apply filters
    if specialization:
        query = query.filter(Doctor.specializations.contains([specialization]))
    if hospital:
        query = query.filter(Doctor.hospital_affiliations.contains([hospital]))
    if name:
        query = query.filter(Doctor.name.ilike(f'%{name}%'))
    if location:
        # Join with chambers and filter by location
        query = query.join(Doctor.chambers).filter(
            Chamber.location.ilike(f'%{location}%')
        )

    doctors = query.all()
    return jsonify(doctors_schema.dump(doctors))


@bp.route('/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return jsonify(doctor_schema.dump(doctor))


@bp.route('', methods=['POST'])
@jwt_required()
def create_doctor():
    data = request.get_json()

    new_doctor = Doctor(
        name=data['name'],
        contact_number=data['contact_number'],
        specializations=data.get('specializations', []),
        hospital_affiliations=data.get('hospital_affiliations', []),
        degrees=data.get('degrees', [])
    )

    db.session.add(new_doctor)
    db.session.commit()

    return jsonify(doctor_schema.dump(new_doctor)), 201


@bp.route('/<int:doctor_id>', methods=['PUT'])
@jwt_required()
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.get_json()

    for field in ['name', 'contact_number', 'specializations',
                  'hospital_affiliations', 'degrees']:
        if field in data:
            setattr(doctor, field, data[field])

    db.session.commit()
    return jsonify(doctor_schema.dump(doctor))