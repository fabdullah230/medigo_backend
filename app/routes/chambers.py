# app/routes/chambers.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Chamber, Schedule, db
from app.schemas import ChamberSchema, ScheduleSchema

bp = Blueprint('chambers', __name__, url_prefix='/chambers')
chamber_schema = ChamberSchema()
chambers_schema = ChamberSchema(many=True)
schedule_schema = ScheduleSchema()


@bp.route('', methods=['GET'])
def get_chambers():
    # Get query parameters
    location = request.args.get('location')
    doctor_id = request.args.get('doctor_id')

    query = Chamber.query

    if location:
        query = query.filter(Chamber.location.ilike(f'%{location}%'))
    if doctor_id:
        query = query.join(Chamber.doctors).filter_by(id=doctor_id)

    chambers = query.all()
    return jsonify(chambers_schema.dump(chambers))


@bp.route('/<int:chamber_id>', methods=['GET'])
def get_chamber(chamber_id):
    chamber = Chamber.query.get_or_404(chamber_id)
    return jsonify(chamber_schema.dump(chamber))


@bp.route('', methods=['POST'])
@jwt_required()
def create_chamber():
    data = request.get_json()

    # Create schedule first if provided
    schedule = None
    if 'schedule' in data:
        schedule = Schedule(time_slots=data['schedule'])
        db.session.add(schedule)
        db.session.flush()

    new_chamber = Chamber(
        location=data['location'],
        schedule_id=schedule.id if schedule else None
    )

    # Add doctors if provided
    if 'doctor_ids' in data:
        doctors = Doctor.query.filter(Doctor.id.in_(data['doctor_ids'])).all()
        new_chamber.doctors.extend(doctors)

    # Add operators if provided
    if 'operator_ids' in data:
        operators = User.query.filter(User.id.in_(data['operator_ids'])).all()
        new_chamber.operators.extend(operators)

    db.session.add(new_chamber)
    db.session.commit()

    return jsonify(chamber_schema.dump(new_chamber)), 201


@bp.route('/<int:chamber_id>', methods=['PUT'])
@jwt_required()
def update_chamber(chamber_id):
    chamber = Chamber.query.get_or_404(chamber_id)
    data = request.get_json()

    if 'location' in data:
        chamber.location = data['location']

    if 'schedule' in data and chamber.schedule_id:
        schedule = Schedule.query.get(chamber.schedule_id)
        schedule.time_slots = data['schedule']

    if 'doctor_ids' in data:
        doctors = Doctor.query.filter(Doctor.id.in_(data['doctor_ids'])).all()
        chamber.doctors = doctors

    if 'operator_ids' in data:
        operators = User.query.filter(User.id.in_(data['operator_ids'])).all()
        chamber.operators = operators

    db.session.commit()
    return jsonify(chamber_schema.dump(chamber))


@bp.route('/<int:chamber_id>/schedule', methods=['GET'])
def get_chamber_schedule(chamber_id):
    chamber = Chamber.query.get_or_404(chamber_id)
    if not chamber.schedule_id:
        return jsonify({'error': 'No schedule found'}), 404

    schedule = Schedule.query.get(chamber.schedule_id)
    return jsonify(schedule_schema.dump(schedule))