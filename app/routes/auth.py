# app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, db
from app.schemas import UserSchema
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')
user_schema = UserSchema()


@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    # Check if user already exists
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already registered'}), 400

    if User.query.filter_by(contact_number=data.get('contact_number')).first():
        return jsonify({'error': 'Contact number already registered'}), 400

    # Create new user
    new_user = User(
        name=data.get('name'),
        email=data.get('email'),
        contact_number=data.get('contact_number'),
        auth_number=data.get('auth_number'),
        address=data.get('address'),
        bkash_number=data.get('bkash_number'),
        identifying_document_id=data.get('identifying_document_id'),
        precondition_keywords=data.get('precondition_keywords', [])
    )

    db.session.add(new_user)
    db.session.commit()

    # Create access token
    access_token = create_access_token(identity=new_user.id)

    return jsonify({
        'message': 'User created successfully',
        'access_token': access_token,
        'user': user_schema.dump(new_user)
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Support both email and phone number login
    user = User.query.filter(
        (User.email == data.get('username')) |
        (User.contact_number == data.get('username'))
    ).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # In a real implementation, verify the auth_number or implement proper authentication
    # This is a simplified version
    access_token = create_access_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'user': user_schema.dump(user)
    }), 200


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a real implementation, you might want to blacklist the token
    return jsonify({'message': 'Successfully logged out'}), 200