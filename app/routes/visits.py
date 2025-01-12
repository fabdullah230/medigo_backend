# app/routes/visits.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Visit, Doctor, Chamber, User, db
from app.schemas import VisitSchema, VisitDocumentSchema
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

bp = Blueprint('visits', __name__, url_prefix='/visits')
visit_schema = VisitSchema()
visits_schema = VisitSchema(many=True)
visit_document_schema = VisitDocumentSchema()


def check_time_slot_available(chamber_id, doctor_id, appointment_time):
    # Check if the time slot is available
    existing_visit = Visit.query.filter(
        and_(
            Visit.chamber_id == chamber_id,
            Visit.doctor_id == doctor_id,
            Visit.appointment_time == appointment_time,
            Visit.visit_status.in_(['scheduled', 'confirmed'])
        )
    ).first()

    return existing_visit is None


@bp.route('', methods=['GET'])
@jwt_required()
def get_visits():
    user_id = request.args.get('user_id')
    doctor_id = request.args.get('doctor_id')
    status = request.args.get('status')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    query = Visit.query

    if user_id:
        query = query.filter(
            or_(
                Visit.booking_user_id == user_id,
                Visit.patient_user_id == user_id
            )
        )

    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)

    if status:
        query = query.filter_by(visit_status=status)

    if from_date:
        query = query.filter(Visit.appointment_time >= datetime.fromisoformat(from_date))

    if to_date:
        query = query.filter(Visit.appointment_time <= datetime.fromisoformat(to_date))

    visits = query.order_by(Visit.appointment_time.desc()).all()
    return jsonify(visits_schema.dump(visits))


@bp.route('/<int:visit_id>', methods=['GET'])
@jwt_required()
def get_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    return jsonify(visit_schema.dump(visit))


@bp.route('', methods=['POST'])
@jwt_required()
def create_visit():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # Validate doctor and chamber
    doctor = Doctor.query.get_or_404(data['doctor_id'])
    chamber = Chamber.query.get_or_404(data['chamber_id'])

    # Validate patient
    patient_user_id = data.get('patient_user_id', current_user_id)
    if patient_user_id != current_user_id:
        # Check if patient is a dependent of current user
        patient = User.query.get_or_404(patient_user_id)
        if patient.primary_user_id != current_user_id:
            return jsonify({'error': 'Unauthorized to book for this patient'}), 403

    # Check time slot availability
    appointment_time = datetime.fromisoformat(data['appointment_time'])
    if not check_time_slot_available(data['chamber_id'], data['doctor_id'], appointment_time):
        return jsonify({'error': 'Time slot not available'}), 400

    new_visit = Visit(
        chamber_id=data['chamber_id'],
        doctor_id=data['doctor_id'],
        booking_user_id=current_user_id,
        patient_user_id=patient_user_id,
        booking_remarks=data.get('booking_remarks'),
        appointment_time=appointment_time,
        visit_cost=data.get('visit_cost'),
        visit_status='scheduled'
    )

    db.session.add(new_visit)
    db.session.commit()

    return jsonify(visit_schema.dump(new_visit)), 201


@bp.route('/<int:visit_id>', methods=['PUT'])
@jwt_required()
def update_visit(visit_id):
    current_user_id = get_jwt_identity()
    visit = Visit.query.get_or_404(visit_id)
    data = request.get_json()

    # Check authorization
    if visit.booking_user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Handle rescheduling
    if 'appointment_time' in data:
        new_time = datetime.fromisoformat(data['appointment_time'])
        if not check_time_slot_available(visit.chamber_id, visit.doctor_id, new_time):
            return jsonify({'error': 'New time slot not available'}), 400
        visit.appointment_time = new_time
        visit.visit_status = 'rescheduled'

    # Update other fields
    allowed_fields = ['booking_remarks', 'visit_status', 'visit_cost', 'cancel_reason']
    for field in allowed_fields:
        if field in data:
            setattr(visit, field, data[field])

    db.session.commit()
    return jsonify(visit_schema.dump(visit))


@bp.route('/<int:visit_id>', methods=['DELETE'])
@jwt_required()
def cancel_visit(visit_id):
    current_user_id = get_jwt_identity()
    visit = Visit.query.get_or_404(visit_id)

    if visit.booking_user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    visit.visit_status = 'cancelled'
    visit.cancel_reason = request.json.get('cancel_reason')

    db.session.commit()
    return jsonify({'message': 'Visit cancelled successfully'})


@bp.route('/<int:visit_id>/documents', methods=['POST'])
@jwt_required()
def upload_documents(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    data = request.get_json()

    # In a real implementation, handle file uploads to a document storage service
    # For now, we'll just store document metadata
    if not visit.visit_document_ids:
        visit.visit_document_ids = []

    visit.visit_document_ids.append({
        'id': data['document_id'],
        'type': data['document_type'],
        'upload_time': datetime.utcnow().isoformat()
    })

    db.session.commit()
    return jsonify({'message': 'Document uploaded successfully'})


@bp.route('/<int:visit_id>/documents', methods=['GET'])
@jwt_required()
def get_documents(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    return jsonify(visit.visit_document_ids or [])


@bp.route('/<int:visit_id>/prescription', methods=['POST'])
@jwt_required()
def create_prescription(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    data = request.get_json()

    # In a real implementation, validate that the current user is the doctor
    visit.visit_prescription = data
    visit.visit_status = 'completed'

    db.session.commit()
    return jsonify({'message': 'Prescription created successfully'})


@bp.route('/<int:visit_id>/prescription', methods=['GET'])
@jwt_required()
def get_prescription(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    if not visit.visit_prescription:
        return jsonify({'error': 'No prescription found'}), 404
    return jsonify(visit.visit_prescription)