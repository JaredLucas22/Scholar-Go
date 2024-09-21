from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, Sponsorship_data
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

def follow_sponsorship(user_id, sponsorship_id):
    user = User.query.get(user_id)
    sponsorship = Sponsorship_data.query.get(sponsorship_id)

    if not user or not sponsorship:
        return False  # User or sponsorship not found

    if sponsorship not in user.followed_sponsorships:
        user.followed_sponsorships.append(sponsorship)
        db.session.commit()
        return True  # Successfully followed
    return False  # Already following

def unfollow_sponsorship(user_id, sponsorship_id):
    user = User.query.get(user_id)
    sponsorship = Sponsorship_data.query.get(sponsorship_id)

    if not user or not sponsorship:
        return False  # User or sponsorship not found

    if sponsorship in user.followed_sponsorships:
        user.followed_sponsorships.remove(sponsorship)
        db.session.commit()
        return True  # Successfully unfollowed
    return False  # Not currently following

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        course = request.form.get('course')
        gpa = request.form.get('gpa')
        extracurricular_activities = request.form.get('extracurricularActivities')
        financial_status = request.form.get('financialStatus')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                course=course,
                password=generate_password_hash(password1, method='pbkdf2:sha256'),
                gpa=gpa,
                extracurricular_activities=extracurricular_activities,
                financial_status=financial_status
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/sign-sponsor', methods=['GET', 'POST'])
def sign_sponsor():
    if request.method == 'POST':
        sponsor_name = request.form.get('sponsor-name')
        course = request.form.get('course')
        extracurricular_activity = request.form.get('extracurricularActivities')
        weight_fos = float(request.form.get('weight_fos'))
        weight_gpa = float(request.form.get('weightgpa'))
        weight_extracurricular = float(request.form.get('weightextracurricularActivities'))
        weight_financial = float(request.form.get('weightfinancialStatus'))
        passing_requirement = float(request.form.get('passingrequirement'))
        description = request.form.get('description')
        full_description = request.form.get('fulldescription')

        new_sponsor = Sponsorship_data(
            sponsor_name=sponsor_name,
            course=course,
            weight_fos=weight_fos,
            weight_gpa=weight_gpa,
            weight_extracurricular_activities=weight_extracurricular,
            weight_financial_status=weight_financial,
            passing_requirement=passing_requirement,
            description=description,
            full_description=full_description,
            extracurricular_activity=extracurricular_activity,
            verified=False
        )

        db.session.add(new_sponsor)
        db.session.commit()

        flash('Sponsor added successfully!')
        return redirect(url_for('auth.login'))

    return render_template("sign_sponsor.html", user=current_user)

@auth.route('/follow/<int:sponsorship_id>', methods=['POST'])
@login_required
def follow(sponsorship_id):
    # Check if the user is currently following the sponsorship
    if current_user.is_following(sponsorship_id):  # Assuming you have this method defined
        unfollow_sponsorship(current_user.id, sponsorship_id)
        flash('You have unfollowed this sponsorship.', category='success')
    else:
        follow_sponsorship(current_user.id, sponsorship_id)
        flash('You are now following this sponsorship!', category='success')

    return redirect(request.referrer or url_for('views.home'))


