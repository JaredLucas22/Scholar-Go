from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_socketio import emit
from .models import User, Sponsorship_data, user_sponsorship, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db, socketio  # Import socketio here
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import os

auth = Blueprint('auth', __name__)

import os
from flask import current_app

@login_required
@auth.route('/sponsor_details/<int:sponsor_id>', methods=['GET'])
def view_sponsorship(sponsor_id):
    sponsor = Sponsorship_data.query.get_or_404(sponsor_id)
    comments = Comment.query.filter_by(sponsor_id=sponsor_id).all()  # Assuming you have a Comment model
    is_liked = current_user in sponsor.likes
    return render_template('sponsor_details.html', user=current_user, sponsor=sponsor, is_liked=is_liked)


def save_picture(form_picture):
    # Get the original filename
    original_filename = form_picture.filename
    # Ensure the filename is safe and create a unique filename
    filename = original_filename  # You could also append a timestamp if needed
    picture_path = os.path.join(current_app.root_path, 'static/uploads', filename)
    
    # Save the picture
    form_picture.save(picture_path)

    return filename


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
        # Retrieve form data
        sponsor_name = request.form.get('sponsor-name')
        course = request.form.get('course')
        weight_fos = request.form.get('weight_fos', type=float)
        weight_gpa = request.form.get('weightgpa', type=float)
        weight_extracurricular = request.form.get('weightextracurricularActivities', type=float)
        weight_financial = request.form.get('weightfinancialStatus', type=float)
        passing_requirement = request.form.get('passingrequirement', type=float)
        description = request.form.get('description')
        full_description = request.form.get('fulldescription')
        extracurricular_activity = request.form.get('extracurricularActivities')
        amount_per_semester = request.form.get('amount_per_semester', type=float)
        deadline_date_str = request.form.get('deadline_date')  # Get the date input from the form

        # Convert it directly into a date object
        deadline_date = datetime.strptime(deadline_date_str, '%Y-%m-%d').date() if deadline_date_str else None
        
        # Check if the deadline_date is None or invalid before proceeding
        if not deadline_date:
            flash('Deadline date is required.', category='error')
            return redirect(url_for('auth.sign_sponsor'))

        try:
            picture_path = save_picture(request.files.get('picture'))
        except ValueError as e:
            flash(str(e), category='error')
            return redirect(url_for('auth.sign_sponsor'))

        # Create new Sponsorship_data object without additional validation
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
            verified=False,
            amount_per_semester=amount_per_semester,
            deadline_date=deadline_date,  # Ensure this is a valid date
            picture_path=picture_path  # Save the picture path here
        )

        try:
            db.session.add(new_sponsor)
            db.session.commit()
            flash('Sponsor added successfully!')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()  # Roll back the session on error
            print(e)  # Log the error for debugging
            flash('An error occurred while adding the sponsor. Please try again.', category='error')
            return redirect(url_for('auth.sign_sponsor'))

    return render_template("sign_sponsor.html", user=current_user)

@auth.route('/follow/<int:sponsorship_id>', methods=['POST'])
@login_required
def follow(sponsorship_id):
    sponsorship = Sponsorship_data.query.get(sponsorship_id)
    if not sponsorship:
        flash('Sponsorship not found.', category='error')
        return redirect(url_for('views.home'))

    # Check if the user is currently following the sponsorship
    if current_user.is_following(sponsorship_id):
        # Unfollow the sponsorship
        if unfollow_sponsorship(current_user.id, sponsorship_id):
            flash('You have unfollowed this sponsorship!', category='success')
            socketio.emit('unfollow_notification', {
                'message': f"You unfollowed {sponsorship.sponsor_name}.",
                'user_id': current_user.id,
                'sponsorship_id': sponsorship.id
            })
        else:
            flash('Error unfollowing sponsorship. Please try again.', category='error')
    else:
        # Follow the sponsorship
        if follow_sponsorship(current_user.id, sponsorship_id):
            flash('You are now following this sponsorship!', category='success')
            socketio.emit('follow_notification', {
                'message': f"You are now following {sponsorship.sponsor_name}.",
                'user_id': current_user.id,
                'sponsorship_id': sponsorship.id
            })
        else:
            flash('Error following sponsorship. Please try again.', category='error')

    return redirect(request.referrer or url_for('views.home'))


@auth.route('/like/<int:sponsor_id>', methods=['POST'])
@login_required
def like_sponsorship(sponsor_id):
    # Your logic to like/unlike the sponsorship
    if current_user.is_authenticated:
        sponsorship = Sponsorship_data.query.get(sponsor_id)
        if sponsorship:
            if current_user in sponsorship.likes:  # Assuming likes is a relationship
                sponsorship.likes.remove(current_user)
            else:
                sponsorship.likes.append(current_user)
            db.session.commit()
    return redirect(request.referrer or url_for('views.home'))

@auth.route('/add_comment/<int:sponsor_id>', methods=['POST'])
@login_required
def add_comment(sponsor_id):
    content = request.form.get('content')

    # Check if content is empty
    if not content:
        flash('Comment cannot be empty.', 'danger')
        return redirect(request.referrer or url_for('views.home'))

    new_comment = Comment(content=content, user_id=current_user.id, sponsorship_id=sponsor_id)

    try:
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')

    return redirect(request.referrer or url_for('views.home'))

