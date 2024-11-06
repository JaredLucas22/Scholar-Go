from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, session
from flask_socketio import emit
from .models import User, Sponsorship_data, user_sponsorship, Comment, TriggerWord, Notification, user_sponsorship_visits, user_sponsorship_alarm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db, socketio  # Import socketio here
from sqlalchemy import insert
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta, timezone
import os
from .utils import utc_plus_8 
import time
from flask_login import LoginManager
from .models import User, Sponsorship_data
import smtplib
from email.message import EmailMessage
import logging
from threading import Thread

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@auth.route('/api/due_alarms', methods=['GET'])
def notify_due_alarms():
    now = datetime.now(timezone.utc).astimezone(utc_plus_8)
    logger.info(f"Checking alarms at {now}")

    due_alarms = db.session.query(user_sponsorship_alarm).filter(
        user_sponsorship_alarm.c.alarm_time <= now
    ).all()

    if not due_alarms:
        logger.info("No due alarms found.")
        return jsonify({"message": "No due alarms found.", "success": True, "alarms": []})

    # List to hold the messages for response
    alarm_messages = []

    for alarm in due_alarms:
        # Emit real-time notification to the user via Socket.IO
        socketio.emit('alarm_notification', {
            'user_id': alarm.user_id,
            'message': alarm.message,
            'priority': alarm.priority
        }, namespace='/notifications')

        # Add the notification to the notifications table using the add_notification function
        add_notification(user=User.query.get(alarm.user_id), message=alarm.message, sponsorship_id=alarm.sponsorship_id)

        # Collect the message for response
        alarm_messages.append({
            'user_id': alarm.user_id,
            'message': alarm.message,
            'priority': alarm.priority
        })

    # Bulk delete the due alarms after notifying
    db.session.query(user_sponsorship_alarm).filter(
        user_sponsorship_alarm.c.alarm_time <= now
    ).delete(synchronize_session='fetch')

    # Commit changes
    db.session.commit()
    logger.info("All due alarms have been notified and deleted.")

    return jsonify({"message": "Notifications sent for all due alarms.", "success": True, "alarms": alarm_messages})

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

@auth.route('/visit_sponsorship/<int:sponsorship_id>', methods=['POST'])
@login_required
def visit_sponsorship(sponsorship_id):
    print(f"Visit sponsorship called with ID: {sponsorship_id}")  # Debug statement
    user_id = current_user.id
    
    # Insert a new visit record with the current timestamp
    new_visit = {
        'user_id': user_id,
        'sponsorship_id': sponsorship_id,
        'created_at': datetime.now(timezone.utc).astimezone(utc_plus_8)  # Set the current timestamp
    }
    
    try:
        db.session.execute(user_sponsorship_visits.insert().values(new_visit))
        db.session.commit()
        print("New visit logged.")
    except Exception as e:
        db.session.rollback()  # Rollback the session on error
        print(f"Error logging visit: {e}")
        return jsonify({'success': False, 'error': 'Failed to log visit.'}), 500

    # Fetch the sponsorship to get the URL
    sponsor = Sponsorship_data.query.get_or_404(sponsorship_id)
    return jsonify({'success': True, 'url': sponsor.url}), 200



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
        db.session.commit()  # Commit the changes
        print("Sponsorship unfollowed successfully.")
        return jsonify({'success': True, 'message': 'Sponsorship removed successfully.'}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Error while unfollowing sponsorship: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Try to find the email in the User table
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            session['user_type'] = 'User'  # Store user type as 'User' in the session
            return redirect(url_for('views.home'))
        
        # Try to find the email in the Sponsorship_data table
        sponsorship = Sponsorship_data.query.filter_by(email=email).first()
        if sponsorship and check_password_hash(sponsorship.password, password):
            login_user(sponsorship, remember=True)
            session['user_type'] = 'Sponsorship'  # Store user type as 'Sponsorship' in the session
            return redirect(url_for('views.home'))  # Redirect to home for common handling
        
        # If no match found in both tables
        flash('Invalid email or password.', category='error')

    return render_template("login.html", user=current_user)




from flask import current_app
from itsdangerous import URLSafeTimedSerializer
import os
from flask_login import current_user

@auth.route('/test-notification')
@login_required
def test_notification():
    try:
        # Manually add a notification for the current user
        add_notification(current_user, "Almost there.")
        
        # Debug print statement
        print(f"Test Notification added for User {current_user.id}: This is a test notification.")
        
        # Return a response confirming the test
        return jsonify({"success": True, "message": "Test notification added successfully."}), 200
    except Exception as e:
        print(f"Error adding test notification: {str(e)}")
        return jsonify({"success": False, "message": "Failed to add test notification."}), 500

@auth.route('/notify_alarms', methods=['GET'])
@login_required
def notify_alarm():
    try:
        now = datetime.now(timezone.utc).astimezone(utc_plus_8)
        logger.info(f"Current UTC time: {now}")

        # Get all alarms that are due for all users
        alarms = db.session.query(user_sponsorship_alarm).filter(
            user_sponsorship_alarm.c.alarm_time <= now
        ).all()

        # Log retrieved alarms for debugging
        logger.debug(f"Retrieved alarms: {alarms}")

        if not alarms:
            logger.info("No alarms to notify for any users.")
            return jsonify({"success": True, "message": "No alarms to notify."})

        # Notify for each alarm
        for alarm in alarms:
            user_id = alarm.user_id  # Ensure user_id exists in the alarm record
            message = f"Alarm for Sponsorship {alarm.sponsorship_id} is due."
            user = db.session.query(User).filter_by(id=user_id).first()  # Fetch the user based on user_id
            
            if user:
                add_notification(user, message)  # Send notification to the user
                logger.info(f"Notification sent for Alarm: {message} to User ID: {user_id}")

                # Delete the alarm after notifying
                db.session.delete(alarm)

        db.session.commit()  # Commit the changes if you modified the alarms
        logger.info("All due alarms have been notified and deleted successfully.")

        return jsonify({"success": True, "message": "Notifications sent for all due alarms."})

    except Exception as e:
        db.session.rollback()  # Rollback on error
        logger.error(f"Error notifying alarms: {str(e)}")  # Log the error
        return jsonify({"success": False, "message": "An error occurred while notifying alarms."}), 500



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

    # Render the notifications template and pass the notifications and unread_count
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


def add_notification(user, message, sponsorship_id=1):
    notification = Notification(
        user_id=user.id,
        message=message,
        sponsorship_id=sponsorship_id  # Include sponsorship_id if provided
    )
    db.session.add(notification)
    db.session.commit()
    # Debug output
    print(f"Notification added: {notification.message} for user {user.id}")


@auth.route('/notify_all_alarms', methods=['GET'])
@login_required
def notify_all_alarms():
    try:

        now = datetime.now(timezone.utc).astimezone(utc_plus_8)
        logger.info(f"Current time in UTC+8: {now}")

        # Get all alarms that are due for all users
        alarms = db.session.query(user_sponsorship_alarm).filter(
            user_sponsorship_alarm.c.alarm_time <= now
        ).all()

        # Log all retrieved alarms for debugging
        logger.debug(f"Retrieved alarms: {alarms}")

        if not alarms:
            logger.info("No alarms to notify for any users.")
            return jsonify({"success": True, "message": "No alarms to notify."})

        # Notify for each alarm
        for alarm in alarms:
            # Extract user_id and sponsorship_id from the alarm row
            user_id = alarm.user_id
            sponsorship_id = alarm.sponsorship_id

            # Fetch the user and sponsorship details
            user = db.session.query(User).filter_by(id=user_id).first()
            sponsorship = db.session.query(Sponsorship_data).filter_by(id=sponsorship_id).first()

            if user and sponsorship:
                message = f"Alarm for Sponsorship {sponsorship.id} is due."
                add_notification(user, message)  # Notify the actual user
                logger.info(f"Notification sent for Alarm: {message} to User ID: {user.id}")

                # Delete the alarm after notifying
                db.session.query(user_sponsorship_alarm).filter_by(user_id=user_id, sponsorship_id=sponsorship_id).delete()

        db.session.commit()  # Commit the changes if you modified the alarms
        logger.info("All due alarms have been notified and deleted successfully.")

        return jsonify({"success": True, "message": "Notifications sent for all due alarms."})

    except Exception as e:
        db.session.rollback()  # Rollback on error
        logger.error(f"Error notifying alarms: {str(e)}")  # Log the error
        return jsonify({"success": False, "message": "An error occurred while notifying alarms."}), 500



@auth.route('/set_alarm/<int:sponsorship_id>', methods=['POST'])
@login_required
def set_alarm(sponsorship_id):
    try:
        # Get data from the request
        alarm_time_str = request.json.get('alarm_time')
        priority = request.json.get('priority')
        message = request.json.get('message')
        user_id = current_user.id

        print(f"Received data: alarm_time={alarm_time_str}, priority={priority}, user_id={user_id}, sponsorship_id={sponsorship_id}")

        # Check if required fields are present
        if not alarm_time_str or not priority:
            return jsonify({"success": False, "message": "Missing required fields."}), 400

        # Parse the alarm time
        try:
            alarm_time = datetime.strptime(alarm_time_str, '%Y-%m-%d %H:%M:%S')
        except ValueError as ve:
            return jsonify({"success": False, "message": f"Invalid date format: {str(ve)}"}), 400

        # Check if an alarm already exists for this user and sponsorship
        existing_alarm = db.session.query(user_sponsorship_alarm).filter_by(
            user_id=user_id,
            sponsorship_id=sponsorship_id
        ).first()

        if existing_alarm:
            # Update the existing alarm in the database directly
            db.session.query(user_sponsorship_alarm).filter_by(
                user_id=user_id,
                sponsorship_id=sponsorship_id
            ).update({
                'alarm_time': alarm_time,
                'message': message,
                'priority': priority,
                'is_alarm_set': True
            })
            db.session.commit()
            return jsonify({"success": True, "message": "Alarm updated successfully."}), 200

        # If no existing alarm, create a new one
        stmt = insert(user_sponsorship_alarm).values(
            user_id=user_id,
            sponsorship_id=sponsorship_id,
            alarm_time=alarm_time,
            message=message,
            priority=priority,
            is_alarm_set=True
        )

        db.session.execute(stmt)
        db.session.commit()
        print("Alarm added successfully.")
        return jsonify({"success": True, "message": "Alarm set successfully."}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error setting alarm: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while setting the alarm."}), 500



@auth.route('/test_alarm', methods=['POST'])
@login_required
def test_alarm():
    try:
        new_alarm = {
            'user_id': current_user.id,
            'sponsorship_id': 1,  # Replace with a valid ID for testing
            'alarm_time': datetime.now(timezone.utc).astimezone(utc_plus_8),
            'message': "Test alarm"
        }
        db.session.execute(insert(user_sponsorship_alarm).values(new_alarm))
        db.session.commit()
        print("Alarm added successfully.")
        return jsonify({"success": True, "message": "Test alarm added successfully."})
    except Exception as e:
        db.session.rollback()
        print(f"Error adding test alarm: {str(e)}")
        return jsonify({"success": False, "message": "Failed to add test alarm."}), 500

@auth.route('/api/notifications/read/all', methods=['POST'])
@login_required
def mark_all_notifications_as_read():
    # Fetch all notifications for the current user
    user_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    
    if not user_notifications:
        return '', 204  # No content, already marked as read

    for notification in user_notifications:
        notification.is_read = True
    
    db.session.commit()
    return '', 200  # Successfully marked as read


@auth.route('/api/notifications')
@login_required
def api_notifications():
    # Get notifications for the current user
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Count unread notifications
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # Include sponsorship_id in the response
    notifications_data = [{
        'id': notification.id,
        'message': notification.message,
        'is_read': notification.is_read,
        'sponsorship_id': notification.sponsorship_id  # Add sponsorship_id here
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
        confirm_password = request.form.get('confirm_password')  # Get the confirmation password

        # Check if the new password is valid
        if not new_password or new_password.strip() == "":
            flash('Please provide a new password.', category='error')
            return render_template('reset_password.html', user=current_user, token=token)

        # Check if the passwords match
        if new_password != confirm_password:
            flash('Passwords do not match! Please try again.', category='error')
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
        email = request.form.get("SignUpEmail").lower() if request.form.get("SignUpEmail") else None
        # Capture form data
        try:
            first_name = request.form.get('firstName')
            username = request.form.get("username").lower() if request.form.get("username") else None
            last_name = request.form.get('lastName')
            city = request.form.get("city").lower() if request.form.get("city") else None
            province = request.form.get("province").lower() if request.form.get("province") else None
            postalcode = request.form.get('postalcode')
            gender = request.form.get('gender')
            course = request.form.get('course')
            gpa = request.form.get('gpa')
            extracurricular_activities = request.form.get('extracurricularActivities')
            financial_status = request.form.get('financialStatus')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            educationlevel = request.form.get('educationlevel')
            phone_number = request.form.get('phoneNumber')

            # Log form data (excluding sensitive data like password)
            logger.info(f"Received sign-up data: first_name={first_name}, last_name={last_name}, "
                        f"username={username}, email={email}, city={city}, province={province}, "
                        f"postalcode={postalcode}, gender={gender}, course={course}, "
                        f"gpa={gpa}, phone_number={phone_number}, educationlevel={educationlevel}, "
                        f"extracurricular_activities={extracurricular_activities}, "
                        f"financial_status={financial_status}")

            # Emit log event to front-end
            socketio.emit('log_event', {'message': f"Received sign-up data for {username}"})

            # Birthdate processing
            birthdate_str = request.form.get('dateOfBirth')
            birthdate = None
            if birthdate_str:
                try:
                    birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
                    logger.info(f"Parsed birthdate: {birthdate}")
                    socketio.emit('log_event', {'message': f"Parsed birthdate: {birthdate}"})
                except ValueError:
                    logger.error(f"Invalid birthdate format: {birthdate_str}")
                    socketio.emit('log_event', {'message': 'Invalid birthdate format. Please use YYYY-MM-DD.'})
                    flash('Invalid birthdate format. Please use YYYY-MM-DD.', category='error')
                    return redirect(url_for('auth.sign_up'))

            # User existence check
            user = User.query.filter_by(email=email).first()

            # Validation checks
            if email is None:
                logger.warning("Email not provided.")
                socketio.emit('log_event', {'message': 'Email must be provided.'})
                flash('Email must be provided.', category='error')
                return redirect(url_for('auth.login'))  # Redirect to login page when email exists
            elif user:
                logger.warning(f"Attempted sign-up with existing email: {email}")
                socketio.emit('log_event', {'message': 'Email already exists.'})
                flash('Email already exists. Please log in.', category='error')
                return redirect(url_for('auth.login'))  # Redirect to login page when email exists
            elif len(email) < 4:
                logger.warning("Email length is less than 4 characters.")
                socketio.emit('log_event', {'message': 'Email must be greater than 3 characters.'})
                flash('Email must be greater than 3 characters.', category='error')
                return redirect(url_for('auth.login'))  # Redirect to login page when email exists
            elif len(first_name) < 2:
                logger.warning("First name length is less than 2 characters.")
                socketio.emit('log_event', {'message': 'First name must be greater than 1 character.'})
                flash('First name must be greater than 1 character.', category='error')
                return redirect(url_for('auth.login'))  # Redirect to login page when email exists
            elif password1 != password2:
                logger.warning("Passwords do not match.")
                socketio.emit('log_event', {'message': "Passwords don't match."})
                flash("Passwords don't match.", category='error')
                return redirect(url_for('auth.login'))  # Redirect to login page when email exists
            elif len(password1) < 7:
                logger.warning("Password length is less than 7 characters.")
                socketio.emit('log_event', {'message': 'Password must be at least 7 characters.'})
                flash('Password must be at least 7 characters.', category='error')
                return redirect(url_for('auth.login'))  # Redirect to login page when email exists
            else:
                # Create new user after all checks pass
                new_user = User(
                    email=email,
                    first_name=first_name,
                    username=username,
                    last_name=last_name,
                    city=city,
                    province=province,
                    postalcode=postalcode,
                    gender=gender,
                    course=course,
                    gpa=gpa,
                    phone_number=phone_number,
                    educationlevel=educationlevel,
                    birthdate=birthdate,
                    extracurricular_activities=extracurricular_activities,
                    financial_status=financial_status,
                    password=generate_password_hash(password1, method='pbkdf2:sha256'),
                    picture_path="default-avatar-icon-of-social-media-user-vector.jpg"
                )
                db.session.add(new_user)
                db.session.commit()

                logger.info(f"New user created: {email} (username: {username})")

                # Log in user and assign user type
                login_user(new_user, remember=True)
                session['user_type'] = new_user.get_user_type()

                # Emit success message to client
                emit('flash_message', {'message': 'Account created successfully!', 'category': 'success'}, broadcast=True, namespace='/notifications')

                return redirect(url_for('views.home'))

        except Exception as e:
            logger.error(f"Sign-up error: {str(e)}", exc_info=True)
            emit('flash_message', {'message': 'An unexpected error occurred. Please try again.', 'category': 'error'}, broadcast=True, namespace='/notifications')
            return redirect(url_for('login.html'))

    return render_template("login.html", user=current_user)


from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
from .models import Sponsorship_data
from . import db



@auth.route('/sign-sponsor', methods=['GET', 'POST'])
def sign_sponsor():
    if request.method == 'POST':
        # Retrieve form data
        sponsor_name = request.form.get('sponsor-name', '').lower()
        persontocontact	= request.form.get('persontocontact	')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        tar_city = request.form.get('tar_city')
        tar_province = request.form.get('tar_province')
        tar_postalcode = request.form.get('tar_postalcode')
        password2 = request.form.get('password2')
        address = request.form.get('address')
        url = request.form.get('url')
        contact_information = request.form.get('contact_information')
        course = request.form.get('course')
        fos = request.form.get('fos')
        weight_fos = request.form.get('weight_fos', type=float)
        weight_course = request.form.get('weight_course', type=float)
        weight_loc = request.form.get('weight_loc', type=float)
        weight_gpa = request.form.get('weightgpa', type=float)
        weight_extracurricular = request.form.get('weightextracurricularActivities', type=float)
        weight_financial = request.form.get('weightfinancialStatus', type=float)
        passing_requirement = request.form.get('passingrequirement', type=float)
        description = request.form.get('description')
        full_description = request.form.get('fulldescription')
        extracurricular_activity = request.form.get('extracurricularActivities')
        deadline_date_str = request.form.get('deadline_date')  # Get the date input from the form
        amount_per_semester = request.form.get('amount_per_semester')

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
            address = address,
            password=generate_password_hash(password1, method='pbkdf2:sha256'),
            course=course,
            url=url,
            persontocontact=persontocontact,
            contact_information=contact_information,
            weight_fos=weight_fos,
            fos = fos,
            weight_loc=weight_loc,
            tar_province = tar_province,
            tar_city = tar_city,
            tar_postalcode = tar_postalcode,
            weight_course=weight_course,
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
            
            # Log in the new sponsor
            login_user(new_sponsor, remember=True)  # Use new_sponsor to log in
            session['user_type'] = 'Sponsorship'  # Store user type as 'Sponsorship' in the session
            flash('Sponsor added successfully!', category='success')
            return redirect(url_for('views.home'))  # Redirect to the sponsor dashboard
        except Exception as e:
            db.session.rollback()  # Roll back on error
            print(e)  # Log error for debugging
            flash('An error occurred while adding the sponsor. Please try again.', category='error')
            return redirect(url_for('auth.sign_sponsor'))  # Redirect to the sign sponsor route
        
    return render_template('sign_sponsor.html', user=current_user)  # Pass current_user to the template



@auth.route('/visit_count/<int:sponsorship_id>', methods=['GET'])
@login_required
def visit_count(sponsorship_id):
    current_year = datetime.now().year

    # Count visits for the current year
    visit_count = db.session.query(user_sponsorship_visits).filter(
        user_sponsorship_visits.c.sponsorship_id == sponsorship_id,
        db.func.strftime('%Y', user_sponsorship_visits.c.created_at) == str(current_year)
    ).count()

    return jsonify({'success': True, 'visit_count': visit_count})


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

@auth.route('/follower_count/<int:sponsorship_id>', methods=['GET'])
@login_required
def follower_count(sponsorship_id):
    sponsorship = Sponsorship_data.query.get_or_404(sponsorship_id)
    follower_count = len(sponsorship.followers)
    return jsonify(success=True, follower_count=follower_count)


@auth.route('/get_likes/<int:sponsor_id>', methods=['GET'])
@login_required
def get_likes(sponsor_id):
    sponsorship = Sponsorship_data.query.get(sponsor_id)
    if sponsorship:
        return jsonify({
            'success': True,
            'likes_count': len(sponsorship.likes)
        })
    return jsonify({'success': False, 'message': 'Sponsorship not found.'}), 404




@auth.route('/like/<int:sponsor_id>', methods=['POST'])
@login_required
def like_sponsorship(sponsor_id):
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'User is not authenticated.'}), 401

    # Retrieve the sponsorship data
    sponsorship = Sponsorship_data.query.get(sponsor_id)
    if not sponsorship:
        return jsonify({'success': False, 'message': 'Sponsorship not found.'}), 404

    # Toggle the like status
    if current_user in sponsorship.likes:
        sponsorship.likes.remove(current_user)
        liked = False
    else:
        sponsorship.likes.append(current_user)
        liked = True

    # Commit the changes to the database
    db.session.commit()

    return jsonify({
        'success': True,
        'is_liked': liked,
        'likes_count': len(sponsorship.likes),
        'message': 'Like status updated successfully!'
    })


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
    province = request.form.get('tar_province')
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

                # Update the profile picture based on user type
                if session.get('user_type') == 'Sponsorship':
                    sponsorship_data = Sponsorship_data.query.filter_by(id=current_user.id).first()
                    sponsorship_data.picture_path = picture_path
                else:  # Assuming it's a regular User
                    current_user.picture_path = picture_path

                # Commit the changes
                db.session.commit()

                flash('Profile picture updated successfully!', category='success'), 500
                return redirect(request.referrer)  # Redirect to profile page

            except ValueError as e:
                flash(str(e), category='error')
                return redirect(request.referrer)  # Redirect on error

    flash('No file uploaded or file is invalid.', category='error'), 500
    return redirect(request.referrer)  # Redirect if no valid picture was uploaded


@auth.route('/update_sponsor_profile', methods=['POST'])
@login_required
def update_sponsor_profile():
    # Check if the user is of type Sponsorship
    if session.get('user_type') == 'Sponsorship':
        # Get form data
        sponsor_name = request.form.get('sponsor_name') # Use 'sponsor_name' to match the input field name
        address = request.form.get('address')
        fos = request.form.get('fos')
        persontocontact = request.form.get('persontocontact')
        course = request.form.get('course')
        email = request.form.get('email')
        contact_information = request.form.get('contact_information')
        amount = request.form.get('amount_per_semester')
        type_of_sponsor = request.form.get('type_of_sponsor')


        # Log the profile update attempt
        logging.info(f'User {current_user.id} is updating their profile.')

        # Update sponsor information
        sponsorship_data = Sponsorship_data.query.filter_by(id=current_user.id).first()
        if sponsorship_data:
            sponsorship_data.sponsor_name = sponsor_name
            sponsorship_data.email = email
            sponsorship_data.fos = fos
            sponsorship_data.course = course
            sponsorship_data.address = address
            sponsorship_data.persontocontact = persontocontact
            sponsorship_data.contact_information = contact_information
            sponsorship_data.type_of_sponsor = type_of_sponsor
            sponsorship_data.amount_per_semester = amount

            # Commit the changes
        try:
            db.session.commit()
            logging.info(f'User {current_user.id} successfully updated their profile.')
            flash('Sponsor profile updated successfully!', category='success')
        except Exception as e:
            db.session.rollback()
            logging.error(f'Error updating profile for user {current_user.id}: {str(e)}')
            flash(f'An error occurred while updating your sponsor profile: {str(e)}. Please try again.', category='error')  # Include the error message for debugging


    return redirect(url_for('views.profile_sponsor'))  # Redirect to the sponsor profile page





