from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Association Table
user_sponsorship = db.Table('user_sponsorship',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('sponsorship_id', db.Integer, db.ForeignKey('sponsorship_data.id'), primary_key=True)
    
)

user_sponsorship_likes = db.Table('user_sponsorship_likes',
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
    username = db.Column(db.String(150), unique=True)
    image = db.Column(db.String(300), nullable=True) 
    city = db.Column(db.String(150))
    birthdate = db.Column(db.Date, nullable=False)
    province = db.Column(db.String(150))
    postalcode = db.Column(db.String(150))
    picture_path = db.Column(db.String(255), nullable=False)  # Ensure this line is present
    educationlevel = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    suffix = db.Column(db.String(150), nullable= True)
    gender = db.Column(db.String(150))
    course = db.Column(db.String(150))
    phone_number = db.Column(db.String(150))
    gpa = db.Column(db.Float)
    extracurricular_activities = db.Column(db.String(300))
    financial_status = db.Column(db.String(150))
    notes = db.relationship('Note', backref='user', lazy=True)
    followed_sponsorships = db.relationship('Sponsorship_data', secondary=user_sponsorship,
                                             lazy='subquery', backref=db.backref('followers', lazy=True))
    comments = db.relationship('Comment', backref='user', lazy=True)

    def is_following(self, sponsorship_id):
        return any(sponsorship.id == sponsorship_id for sponsorship in self.followed_sponsorships)

    def add_follow(self, sponsorship):
        if not self.is_following(sponsorship.id):
            self.followed_sponsorships.append(sponsorship)
            db.session.commit()

    def remove_follow(self, sponsorship):
        if self.is_following(sponsorship.id):
            self.followed_sponsorships.remove(sponsorship)
            db.session.commit()



from sqlalchemy.sql import func

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sponsorship_id = db.Column(db.Integer, db.ForeignKey('sponsorship_data.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())  # Add this line

    



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
    image = db.Column(db.String(300), nullable=True)  # For the uploaded picture
    likes = db.relationship('Like', backref='sponsorship', lazy=True)  # For user likes
    deadline_date = db.Column(db.Date, nullable=False)  # Scholarship deadline
    active = db.Column(db.Boolean, default=True, nullable=False)  # Active or inactive status
    amount_per_semester = db.Column(db.Float, nullable=False)  # Amount awarded per semester
    likes = db.relationship('User', secondary=user_sponsorship_likes, backref='liked_by')
    picture_path = db.Column(db.String(255), nullable=False)  # Ensure this line is present
    comments = db.relationship('Comment', backref='sponsorship')