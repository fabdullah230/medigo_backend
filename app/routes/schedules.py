# app/routes/schedules.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Schedule, Chamber, db
from datetime import datetime, timedelta

bp = Blueprint('schedules', __name__, url_prefix='/schedules')


@bp.route('/chamber/<int:chamber_id>/slots', methods=['POST'])
@jwt_required()
def create_time_slots(chamber_id):
    data = request.get_json()
    chamber = Chamber.query.get_or_404(chamber_id)

    # Create regular schedule
    schedule = Schedule(
        chamber_id=chamber_id,
        time_slots={
            'weekday': data['weekday_slots'],
            'weekend': data['weekend_slots'],
            'exceptions': data.get('exceptions', [])
        }
    )

    db.session.add(schedule)
    chamber.schedule_id = schedule.id
    db.session.commit()

    return jsonify({'message': 'Schedule created successfully'})


@bp.route('/chamber/<int:chamber_id>/available-slots', methods=['GET'])
def get_available_slots(chamber_id):
    date = request.args.get('date')
    doctor_id = request.args.get('doctor_id')

    # Get chamber schedule
    chamber = Chamber.query.get_or_404(chamber_id)
    schedule = Schedule.query.get(chamber.schedule_id)

    # Calculate available slots based on schedule and existing appointments
    # Return list of available time slots

    return jsonify({
        'date': date,
        'available_slots': calculate_available_slots(schedule, date, doctor_id)
    })