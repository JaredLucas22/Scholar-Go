from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_socketio import emit
from .models import User, Sponsorship_data, user_sponsorship, Comment, TriggerWord, Notification
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db, socketio  # Import socketio here
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from flask_login import LoginManager
from .models import User, Sponsorship_data
import smtplib
from email.message import EmailMessage
from datetime import timedelta
import logging

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

email_user = ('jjclucas.student@ua.edu.ph') 
email_password = ('yfxm ejor oqhs phet') 
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return user
    # If not found as a User, try loading as Sponsorship_data
    return Sponsorship_data.query.get(int(user_id))

auth = Blueprint('auth', __name__)
# Define the path to the 'uploads' folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

import os
from flask import current_app

@login_required
@auth.route('/sponsor_details/<int:sponsor_id>', methods=['GET'])
def view_sponsorship(sponsor_id):
    sponsor = Sponsorship_data.query.get_or_404(sponsor_id)

    comments = Comment.query.filter_by(sponsor_id=sponsor_id).order_by(Comment.created_at.desc()).all()
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


@auth.route('/follow/<int:sponsorship_id>', methods=['POST'])
@login_required
def toggle_follow_sponsorship(sponsorship_id):
    sponsorship = Sponsorship_data.query.get(sponsorship_id)
    if not sponsorship:
        return jsonify({"success": False, "message": "Sponsorship not found."}), 404

    # Toggle follow state
    if current_user.is_following(sponsorship_id):
        current_user.remove_follow(sponsorship)
        message = 'You have unfollowed this sponsorship!'
        is_following = False
    else:
        current_user.add_follow(sponsorship)
        message = 'You are now following this sponsorship!'
        is_following = True

    # Prepare the response data
    return jsonify({
        "success": True,
        "message": message,
        "is_following": is_following
    })



@auth.route('/unfollow/<int:sponsorship_id>', methods=['POST'])
@login_required
def unfollow_sponsorship(sponsorship_id):
    print(f"Attempting to unfollow sponsorship ID: {sponsorship_id}")

    # Retrieve the sponsorship data
    sponsorship = Sponsorship_data.query.get(sponsorship_id)
    if not sponsorship:
        print("Sponsorship not found.")
        return jsonify({'success': False, 'message': 'Sponsorship not found.'}), 404

    # Check if the current user is following the sponsorship
    if not current_user.is_following(sponsorship_id):
        print("User is not following this sponsorship.")
        return jsonify({'success': False, 'message': 'You are not following this sponsorship.'}), 400

    try:
        # Attempt to remove the follow
        current_user.remove_follow(sponsorship)
        print("Sponsorship unfollowed successfully.")
        return jsonify({'success': True, 'message': 'Sponsorship removed successfully.'})
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Error while unfollowing sponsorship: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500


from flask_login import current_user, login_user, logout_user

from flask import session

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Try to find the email in the User table
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            session['user_type'] = user.get_user_type()  # Store user type in the session
            return redirect(url_for('views.home'))
        
        # Try to find the email in the Sponsorship_data table
        sponsorship = Sponsorship_data.query.filter_by(email=email).first()
        if sponsorship and check_password_hash(sponsorship.password, password):
            login_user(sponsorship, remember=True)
            session['user_type'] = 'Sponsorship'  # Store user type as 'Sponsorship' in the session
            return redirect(url_for('views.home'))
        
        # If no match found in both tables
        flash('Invalid email or password.', category='error')

    return render_template("login.html", user=current_user)



from flask import current_app
from itsdangerous import URLSafeTimedSerializer
import os
from datetime import timedelta

from flask_login import current_user

@auth.route('/test-notification')
@login_required
def test_notification():
    # Manually add a notification for the current user
    add_notification(current_user, "Almost there.")
    
    # Debug print statement
    print(f"Test Notification added for User {current_user.id}: This is a test notification.")
    
    # Return a response confirming the test
    return render_template ("views.home", user=current_user)


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        # Try to find the email in the User or Sponsorship_data table
        user = User.query.filter_by(email=email).first()
        sponsorship = Sponsorship_data.query.filter_by(email=email).first()

        # Select the correct user
        account = user if user else sponsorship

        if account:
            # Generate a password reset token
            token = generate_reset_token(email)

            # Send password reset email
            subject = "Password Reset Request"
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            body = f"""
            Hello,

            You requested to reset your password. Click the link below to reset your password:
            
            {reset_link}
            
            This link will expire in 24 hours. If you did not make this request, please ignore this email.

            Thank you.
            """
            send_email(subject, body, email)
            flash('Password reset link has been sent to your email.', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email does not exist in the system.', category='error')

    return render_template("forgot_password.html", user=current_user)

@auth.route('/notifications')
@login_required
def notifications():
    # Get all notifications for the current user
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()

    # Mark all unread notifications as read
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    
    # Get the count of unread notifications
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # Commit the session to save changes
    db.session.commit()

    # Render the notifications template and pass unread_count
    return render_template("notifications.html", notifications=user_notifications, unread_count=unread_count, user=current_user)

@auth.route('/notifications/read/<int:notification_id>')
@login_required
def read_notification(notification_id):
        # Get all notifications for the current user
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()

    notification = Notification.query.get(notification_id)
    if notification and notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
    return render_template("notifications.html", user=current_user, notifications=user_notifications)
@auth.route('/notifications/latest')
@login_required
def latest_notifications():
    # Fetch the 5 most recent notifications for the current user
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    notifications_list = [{'id': n.id, 'message': n.message, 'is_read': n.is_read} for n in user_notifications]
    return jsonify(notifications_list)


def add_notification(user, message):
    notification = Notification(message=message, user_id=user.id)  # Save the user_id, not the user object
    db.session.add(notification)
    db.session.commit()
    # Debug output
    print(f"Notification added: {notification.message} for user {user.id}")


@auth.route('/api/notifications')
@login_required
def api_notifications():
    # Get notifications for the current user
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Count unread notifications
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    notifications_data = [{
        'id': notification.id,
        'message': notification.message,
        'is_read': notification.is_read
    } for notification in user_notifications]
    
    return jsonify({'notifications': notifications_data, 'unread_count': unread_count})



@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Redirect authenticated users away from the reset password page
    if current_user.is_authenticated:
        flash('You are already logged in. Please log out to reset your password.', category='error')
        return redirect(url_for('views.home'))

    try:
        # Verify the token and get the email
        email = verify_reset_token(token)
    except Exception as e:
        logging.error(f"Token verification failed: {e}")
        flash('The token is invalid or has expired.', category='error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')  # Get the new password from the form

        # Check if the new password is valid
        if not new_password or new_password.strip() == "":
            flash('Please provide a new password.', category='error')
            return render_template('reset_password.html', user=current_user, token=token)

        # Update the user's password
        user = User.query.filter_by(email=email).first()  # Look up the user in the database
        if user:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()

            flash('Your password has been reset successfully.', category='success')
            return redirect(url_for('auth.login'))
        else:
            logging.warning(f"User not found for email: {email}")  # Log the warning
            flash('User not found. Please check your email.', category='error')

    return render_template('reset_password.html', user=current_user, token=token)


def generate_reset_token(email):
    """Generates a token for resetting password."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def verify_reset_token(token, expiration=86400):
    """Verifies the token and returns the email if valid, otherwise raises an error."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)


def send_email(subject, body, recipient_email):
    if not recipient_email:
        print("Recipient email cannot be None.")
        return
    if not subject:
        print("Email subject cannot be None.")
        return
    if not body:
        print("Email body cannot be None.")
        return
    if not email_user:
        print("Email user cannot be None.")
        return
    if not email_password:
        print("Email password cannot be None.")
        return

    # Set up the email message
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = email_user  # Your email address
    msg['To'] = recipient_email

    # Send the email using SMTP
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


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
        username = request.form.get('username')
        last_name = request.form.get('lastName')
        suffix = request.form.get('suffix')
        city = request.form.get('city')
        province = request.form.get('province')
        postalcode = request.form.get('postalcode')
        gender = request.form.get('gender')
        course = request.form.get('course')
        gpa = request.form.get('gpa')
        extracurricular_activities = request.form.get('extracurricularActivities')
        financial_status = request.form.get('financialStatus')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        educationlevel = request.form.get('educationlevel')
        birthdate = request.form.get('dateOfBirth')
        phone_number = request.form.get('phoneNumber')

                # Inside the sign_up function
        birthdate_str = request.form.get('dateOfBirth')  # This is a string in YYYY-MM-DD format

        # Convert string to date object
        if birthdate_str:
            try:
                birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid birthdate format. Please use YYYY-MM-DD.', category='error')
                return redirect(url_for('auth.sign_up'))
        else:
            birthdate = None  # Handle case where no birthdate is provided
        
        # Handle picture upload
        picture = request.files.get('picture')  # Get the uploaded file
        if picture:
            try:
                picture_path = save_picture(picture)  # Call the function to save the picture
            except ValueError as e:
                flash(str(e), category='error')
                return redirect(url_for('auth.sign_up'))
        else:
            picture_path = None  # Handle case where no picture is uploaded

        # Error handling and validation
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
            # Create new user
            new_user = User(
                email=email,
                first_name=first_name,
                username=username,
                last_name=last_name,
                suffix=suffix,
                city=city,
                province=province,
                postalcode=postalcode,
                gender=gender,
                course=course,
                gpa=gpa,
                phone_number = phone_number,
                educationlevel = educationlevel,
                birthdate = birthdate,
                extracurricular_activities=extracurricular_activities,
                financial_status=financial_status,
                password=generate_password_hash(password1, method='pbkdf2:sha256'),
                picture_path=picture_path  # Save the picture path here
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
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        course = request.form.get('course')
        weight_fos = request.form.get('weight_fos', type=float)
        weight_gpa = request.form.get('weightgpa', type=float)
        weight_extracurricular = request.form.get('weightextracurricularActivities', type=float)
        weight_financial = request.form.get('weightfinancialStatus', type=float)
        passing_requirement = request.form.get('passingrequirement', type=float)
        description = request.form.get('description')
        full_description = request.form.get('fulldescription')
        extracurricular_activity = request.form.get('extracurricularActivities')
        deadline_date_str = request.form.get('deadline_date')  # Get the date input from the form
        
        # Get the amount_per_semester and format it
        amount_per_semester_str = request.form.get('amount_per_semester')
        try:
            amount_per_semester = float(amount_per_semester_str.replace(',', '').strip())  # Remove commas for conversion
            formatted_amount_per_semester = f"{amount_per_semester:,.2f}"  # Format with commas and 2 decimal places
        except (ValueError, TypeError):
            flash('Invalid amount per semester.', category='error')
            return redirect(url_for('auth.sign_sponsor'))

        # Convert it directly into a date object
        deadline_date = datetime.strptime(deadline_date_str, '%Y-%m-%d').date() if deadline_date_str else None

        # Validation checks
        sponsorship = Sponsorship_data.query.filter_by(email=email).first()
        if sponsorship:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(sponsor_name) < 2:
            flash('Sponsor name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif not deadline_date:
            flash('Deadline date is required.', category='error')
            return redirect(url_for('auth.sign_sponsor'))

        # Save the picture and get its path
        try:
            picture_path = save_picture(request.files.get('picture'))
        except ValueError as e:
            flash(str(e), category='error')
            return redirect(url_for('auth.sign_sponsor'))

        # Create a new Sponsorship_data object
        new_sponsor = Sponsorship_data(
            sponsor_name=sponsor_name,
            email=email,
            password=generate_password_hash(password1, method='pbkdf2:sha256'),
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
            amount_per_semester=amount_per_semester,  # Use the raw float value for DB
            deadline_date=deadline_date,  # Ensure this is a valid date
            picture_path=picture_path,  # Save the picture path here
        )

        # Add the new sponsor to the database
        try:
            db.session.add(new_sponsor)
            db.session.commit()
            flash('Sponsor added successfully!', category='success')
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
        current_user.remove_follow(sponsorship)
        flash('You have unfollowed this sponsorship!', category='success')
        socketio.emit('unfollow_notification', {
            'message': f"You unfollowed {sponsorship.sponsor_name}.",
            'user_id': current_user.id,
            'sponsorship_id': sponsorship.id
        })
    else:
        # Follow the sponsorship
        current_user.add_follow(sponsorship)
        flash('You are now following this sponsorship!', category='success')
        socketio.emit('follow_notification', {
            'message': f"You are now following {sponsorship.sponsor_name}.",
            'user_id': current_user.id,
            'sponsorship_id': sponsorship.id
        })

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
                liked = False  # User unliked the sponsorship
            else:
                sponsorship.likes.append(current_user)
                liked = True  # User liked the sponsorship
            
            db.session.commit()

            # Return a JSON response with success status and new likes count
            return jsonify({
                'success': True,
                'is_liked': liked,
                'likes_count': len(sponsorship.likes),
                'message': 'Like status updated successfully!'
            })

    # If sponsorship not found or user is not authenticated, return an error message
    return jsonify({'success': False, 'message': 'An error occurred.'}), 400

@auth.route('/add_comment/<int:sponsor_id>', methods=['POST'])
@login_required
def add_comment(sponsor_id):
    content = request.form.get('content')

    # Fetch all trigger words from the database
    trigger_words = TriggerWord.query.all()
    trigger_word_list = [tw.word.lower() for tw in trigger_words]

    # Check if the comment contains any trigger words
    if any(word in content.lower() for word in trigger_word_list):
        return jsonify({"success": False, "message": "Your comment contains inappropriate words."}), 400

    # Add the comment if no trigger words are found
    new_comment = Comment(content=content, user_id=current_user.id, sponsorship_id=sponsor_id)
    db.session.add(new_comment)
    db.session.commit()

    # Prepare the data to send back in the JSON response
    comment_data = {
        "id": new_comment.id,
        "content": new_comment.content,
        "user_username": current_user.username,
        "user_picture_path": current_user.picture_path,
        "relative_time": "just now",  # Replace with actual calculation if needed
        "timestamp": new_comment.created_at.timestamp()
    }

    # Return a JSON response indicating success and including the comment data
    return jsonify({"success": True, "comment": comment_data}), 200


@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    # Get form data
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    suffix = request.form.get('suffix')
    city = request.form.get('city')
    province = request.form.get('province')
    gender = request.form.get('gender')
    postalcode = request.form.get('postalcode')
    education_level = request.form.get('education_level')
    gpa = request.form.get('gpa')
    course = request.form.get('course')

    # Update user information
    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.username = username
    current_user.email = email
    current_user.phone_number = phone_number
    current_user.suffix = suffix
    current_user.city = city
    current_user.province = province
    current_user.gender = gender
    current_user.postalcode = postalcode
    current_user.education_level = education_level
    current_user.gpa = gpa
    current_user.course = course

    # Commit the changes
    try:
        db.session.commit()
        flash('Profile updated successfully!', category='success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating your profile. Please try again.', category='error')

    return redirect(url_for('views.profile'))


@auth.route('/update_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    # Check if a new profile picture was uploaded
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture and profile_picture.filename != '':
            try:
                # Save the picture
                picture_path = save_picture(profile_picture)
                current_user.picture_path = picture_path

                # Commit the changes (optional here if done in update profile)
                db.session.commit()

                flash('Profile picture updated successfully!', category='success')
                return redirect(url_for('views.profile'))  # Redirect to profile page

            except ValueError as e:
                flash(str(e), category='error')
                return redirect(url_for('views.profile'))  # Redirect on error

    # No picture uploaded, redirect back
    flash('No picture uploaded.', category='warning')
    return redirect(url_for('views.profile'))  # Redirect back if no picture was uploaded

