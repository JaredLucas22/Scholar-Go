from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    course = db.Column(db.String(150))
    gpa = db.Column(db.Float(150))
    extracurricular_activities = db.Column(db.String(300))
    financial_status = db.Column(db.String(150))
    notes = db.relationship('Note')

class Sponsorship_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_name = db.Column(db.String(150))   
    course = db.Column(db.String(150))   
    weight_gpa = db.Column(db.Float(150))
    weight_extracurricular_activities = db.Column(db.String(300))
    weight_financial_status = db.Column(db.String(150))
