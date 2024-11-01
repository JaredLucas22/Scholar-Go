from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime





# Association Table for User Sponsorships
user_sponsorship = db.Table('user_sponsorship',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('sponsorship_id', db.Integer, db.ForeignKey('sponsorship_data.id'), primary_key=True)
)



# Association Table for User Sponsorship Alarms
user_sponsorship_alarm = db.Table('user_sponsorship_alarm',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('sponsorship_id', db.Integer, db.ForeignKey('sponsorship_data.id'), primary_key=True),
    db.Column('priority', db.String(50), nullable=True),
    db.Column('alarm_time', db.DateTime(timezone=True), default=func.now()),
    db.Column('message', db.String(256)),
    db.Column('is_alarm_set', db.Boolean, default=False)  # Add this line for the boolean flag
)


# Association Table for User Likes
user_sponsorship_likes = db.Table('user_sponsorship_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('sponsorship_id', db.Integer, db.ForeignKey('sponsorship_data.id'), primary_key=True)
)

# Association Table for User Sponsorship Visits
user_sponsorship_visits = db.Table('user_sponsorship_visits',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),  # Auto-incrementing primary key
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('sponsorship_id', db.Integer, db.ForeignKey('sponsorship_data.id'), nullable=False),
    db.Column('created_at', db.DateTime(timezone=True), default=func.now()),
)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())  # Ensure this is timezone-aware
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    image = db.Column(db.String(300), nullable=True)
    city = db.Column(db.String(150))
    birthdate = db.Column(db.Date, nullable=False)
    province = db.Column(db.String(150))
    notifications = db.relationship('Notification', backref='user', lazy=True)
    postalcode = db.Column(db.String(150))
    picture_path = db.Column(db.String(255), nullable=False)
    educationlevel = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
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

    def get_user_type(self):
        print("User Type: User")  # Debug print statement
        return "User"

class TriggerWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sponsorship_id = db.Column(db.Integer, db.ForeignKey('sponsorship_data.id'), nullable=False)  # Add this line
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(50), nullable=True)
    alarm_date = db.Column(db.DateTime(timezone=True), nullable=True)  # Make alarm_date timezone-aware
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())  # Store in UTC

    def __init__(self, user_id, sponsorship_id, message, is_read=False, priority=None, alarm_date=None):
        self.user_id = user_id
        self.sponsorship_id = sponsorship_id  # Add this line
        self.message = message
        self.is_read = is_read
        self.priority = priority
        self.alarm_date = alarm_date

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, sponsorship_id={self.sponsorship_id}, message='{self.message}', is_read={self.is_read}, priority='{self.priority}', alarm_date={self.alarm_date}, created_at={self.created_at})>"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sponsorship_id = db.Column(db.Integer, db.ForeignKey('sponsorship_data.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())  # Ensure this is timezone-aware

class Sponsorship_data(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_name = db.Column(db.String(150))
    persontocontact = db.Column(db.String(150), nullable=True)
    course = db.Column(db.String(150))
    url = db.Column(db.String(356), unique=True, nullable=True)
    type_of_sponsor  = db.Column(db.String(150))
    address = db.Column(db.String(150), nullable=True)
    contact_information = db.Column(db.String(150), nullable=True)
    extracurricular_activity = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    weight_fos = db.Column(db.Float)
    weight_gpa = db.Column(db.Float)
    weight_extracurricular_activities = db.Column(db.Float)
    weight_financial_status = db.Column(db.Float)
    passing_requirement = db.Column(db.Float)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text)
    full_description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(300), nullable=True)
    deadline_date = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    amount_per_semester = db.Column(db.Float, nullable=False)
    picture_path = db.Column(db.String(255), nullable=False)
    likes = db.relationship('User', secondary=user_sponsorship_likes, backref='liked_by')
    comments = db.relationship('Comment', backref='sponsorship', lazy=True)

    def get_user_type(self):
        print("User Type: Sponsorship")  # Debug print statement
        return "Sponsorship"

    def get_follower_count(self):
        return len(self.followers)
