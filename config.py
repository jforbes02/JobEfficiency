from flask_sqlalchemy import SQLAlchemy
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
