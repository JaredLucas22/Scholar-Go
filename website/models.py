from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Association Table
user_sponsorship = db.Table('user_sponsorship',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('sponsorship_id', db.Integer, db.ForeignKey('sponsorship_data.id'), primary_key=True)
)

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
    gpa = db.Column(db.Float)
    extracurricular_activities = db.Column(db.String(300))
    financial_status = db.Column(db.String(150))
    notes = db.relationship('Note', backref='user', lazy=True)
    followed_sponsorships = db.relationship('Sponsorship_data', secondary=user_sponsorship,
                                             lazy='subquery', backref=db.backref('followers', lazy=True))
    def is_following(self, sponsorship_id):
        return any(sponsorship.id == sponsorship_id for sponsorship in self.followed_sponsorships)


class Sponsorship_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_name = db.Column(db.String(150))   
    course = db.Column(db.String(150))
    extracurricular_activity = db.Column(db.String(150))
    weight_fos = db.Column(db.Float)
    weight_gpa = db.Column(db.Float)
    weight_extracurricular_activities = db.Column(db.Float)
    weight_financial_status = db.Column(db.Float)
    passing_requirement = db.Column(db.Float)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text)  
    full_description = db.Column(db.Text, nullable=True)
