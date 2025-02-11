#Database Work
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

#configuration settings
db = SQLAlchemy()


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    resumes = db.relationship('Resume', backref='user', lazy=True)
    applications = db.relationship('JobApplication', backref='user',lazy=True)


class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)