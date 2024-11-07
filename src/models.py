import enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserRole(enum.Enum):
    user = "user"
    ngo = "ngo"
    volunteer = "volunteer"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.user)
    profile_image = db.Column(db.String(200), nullable=True)

class UserRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    request_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
