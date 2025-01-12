# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthcare.db'  # Use proper DB in production
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'  # Change in production

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Register blueprints
    from app.routes import auth, users, doctors, chambers, visits
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(doctors.bp)
    app.register_blueprint(chambers.bp)
    app.register_blueprint(visits.bp)

    return app