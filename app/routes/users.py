# app/routes/users.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, db
from app.schemas import UserSchema

bp = Blueprint('users', __name__, url_prefix='/users')
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user_schema.dump(user))


@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    for field in ['name', 'contact_number', 'email', 'address',
                  'bkash_number', 'identifying_document_id',
                  'precondition_keywords']:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return jsonify(user_schema.dump(user))


@bp.route('/<int:user_id>/dependents', methods=['GET'])
@jwt_required()
def get_dependents(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(users_schema.dump(user.dependents))


@bp.route('/<int:user_id>/dependents', methods=['POST'])
@jwt_required()
def add_dependent(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    new_dependent = User(
        name=data.get('name'),
        contact_number=data.get('contact_number'),
        email=data.get('email'),
        is_primary_user=False,
        primary_user_id=user_id,
        precondition_keywords=data.get('precondition_keywords', [])
    )

    db.session.add(new_dependent)
    db.session.commit()

    return jsonify(user_schema.dump(new_dependent)), 201