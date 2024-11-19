from flask import Blueprint, render_template, request, flash, jsonify, session, send_from_directory, current_app
from flask_login import login_required, current_user
from .models import Note, Sponsorship_data, Comment, user_sponsorship_visits, User, user_sponsorship_alarm
from . import db
import os
import json
from scoring import calculate_compatibility_score, match_students_to_sponsorships
from flask import render_template
from .utils import time_since
from datetime import datetime
from flask_socketio import  emit


# Define the views blueprint
views = Blueprint('views', __name__)

from flask import send_from_directory
import os

@views.route('/help')
def react_app():
    # This serves the base template with the React app injected inside it
    return render_template('base.html')


@views.route('/help/<path:path>')
def serve_react_assets(path):
    # If it's not a static file, serve index.html
    if path != '' and not os.path.exists(os.path.join(views.root_path, 'react-template', 'build', 'static', path)):
        return send_from_directory(os.path.join(views.root_path, 'react-template', 'src'), 'App.js')
    return send_from_directory(os.path.join(views.root_path, 'react-template', 'build', 'static'), path)


    
@views.route("/profilesponsor")
@login_required
def profile_sponsor():
    sponsorship_data = None
    if session.get('user_type') == 'Sponsorship':
        sponsorship_data = Sponsorship_data.query.filter_by(id=current_user.id).first()
        print("Sponsorship data:", sponsorship_data)  # Debug statement
    else:
        print("User type is not Sponsorship.")  # Debug statement
    return render_template('profile_sponsor.html', user=current_user, sponsorship_data=sponsorship_data)



@views.route('/sponsor/<int:sponsor_id>', methods=['GET'])
def view_sponsorship(sponsor_id):
    sponsor = Sponsorship_data.query.get_or_404(sponsor_id)

    # Check if the user is authenticated
    if current_user.is_authenticated:
        # Check if the user has visited this sponsorship
        visit_record = db.session.query(user_sponsorship_visits).filter_by(
            user_id=current_user.id,
            sponsorship_id=sponsor_id
        ).first()
        
        is_visited = visit_record is not None
        visit_count = db.session.query(user_sponsorship_visits).filter_by(
            user_id=current_user.id,
            sponsorship_id=sponsor_id
        ).count()  # Get the count of visits

        # Check if the user likes this sponsorship
        is_liked = current_user in sponsor.likes

        # Check if the user is following this sponsorship
        is_following = current_user.is_following(sponsor_id)
    else:
        # If the user is not authenticated, set these values to defaults
        is_visited = False
        visit_count = 0
        is_liked = False
        is_following = False

    # Fetch comments for the sponsor
    comments = Comment.query.filter_by(sponsorship_id=sponsor.id).all()

    # Calculate relative time for comments
    for comment in comments:
        comment.relative_time = time_since(comment.created_at)

    # Get the likes count
    likes_count = len(sponsor.likes)

    return render_template('sponsor_details.html', 
                           sponsor=sponsor, 
                           comments=comments, 
                           is_liked=is_liked,
                           is_following=is_following, 
                           user=current_user,
                           likes_count=likes_count,
                           is_visited=is_visited,  # Pass whether it was visited
                           visit_count=visit_count)  # Pass the visit count

@views.route('/sponsorlist', methods=['GET'])
@login_required
def recommendation():
    # Query to get all sponsorships
    all_sponsors = Sponsorship_data.query.all()  # For the 'All Sponsorships' tab
    
    # Calculate compatibility for 'Recommendations' tab
    compatible_sponsors = [
        {
            'sponsor': sponsor,
            'score': calculate_compatibility_score(current_user, sponsor)
        }
        for sponsor in all_sponsors
        if calculate_compatibility_score(current_user, sponsor) >= sponsor.passing_requirement
    ]
    
    # Get the list of sponsorships followed by the current user
    followed_sponsorship_ids = [sponsorship.id for sponsorship in current_user.followed_sponsorships]
    
    # Add the follow status to compatible sponsors for the 'Recommendations' tab
    sponsors_with_follow_status = [
        {
            'sponsor': item['sponsor'],
            'score': item['score'],
            'is_followed': item['sponsor'].id in followed_sponsorship_ids  # True if the user follows the sponsor
        }
        for item in compatible_sponsors
    ]
    
    return render_template('sponsorlist.html', 
                           user=current_user, 
                           sponsorships=all_sponsors,  # All sponsorships tab data
                           sponsors=sponsors_with_follow_status,  # Recommendations tab data
                           followed_sponsorship_ids=followed_sponsorship_ids)  # For follow buttons

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    current_year = datetime.now().year
    sponsorship_data = None
    matched_applicants_count = 0
    total_applicants_count = 0
    acceptance_rating = 0.0
    total_likes = 0
    visit_count = 0
    follower_count = 0

    # Check user type from session and handle accordingly
    if session.get('user_type') == 'Sponsorship':
        sponsorship_data = Sponsorship_data.query.filter_by(id=current_user.id).first()

        if sponsorship_data:
            # Get total likes for the current sponsorship
            total_likes = len(sponsorship_data.likes)

            # Get follower count using the new method
            follower_count = sponsorship_data.get_follower_count()

            matched_applicants_count, total_applicants_count, acceptance_rating = match_students_to_sponsorships()


            # If matched_applicants_count is a list, use len() to get the count
            if isinstance(matched_applicants_count, list):
                matched_applicants_count = len(matched_applicants_count)

            # Now perform the calculation
            if total_applicants_count > 0:  # Ensure there is no division by zero
                acceptance_rating = (matched_applicants_count / total_applicants_count) * 100
            # Get the visit count for the current sponsorship
            visit_count = db.session.query(user_sponsorship_visits).filter_by(sponsorship_id=sponsorship_data.id).count()
            

        return render_template('sponsor_dashboard.html',
                               visit_count=visit_count,
                               total_likes=total_likes,
                               total_applicants_count=total_applicants_count,
                               user=current_user,
                               sponsorship_data=sponsorship_data,
                               current_year=current_year,
                               matched_applicants_count=matched_applicants_count,
                               acceptance_rating=acceptance_rating,
                               follower_count=follower_count)
    else:
        return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})

@views.route('/follow', methods=['GET'])
@login_required
def follow():
    followed_sponsorships = current_user.followed_sponsorships  # Assuming this relationship is set up in your User model
    
    # Create a list to hold sponsorships along with their alarm status
    sponsorships_with_alarm_status = []

    for sponsorship in followed_sponsorships:
        # Check if the current sponsorship has an alarm set
        alarm_status = db.session.query(user_sponsorship_alarm.c.is_alarm_set).filter(
            user_sponsorship_alarm.c.user_id == current_user.id,
            user_sponsorship_alarm.c.sponsorship_id == sponsorship.id
        ).first()

        # Get the alarm status (True/False), defaulting to False if no record found
        is_alarm_set = alarm_status.is_alarm_set if alarm_status else False
        
        sponsorships_with_alarm_status.append((sponsorship, is_alarm_set))
    
    return render_template("follow.html", sponsorships_with_alarm_status=sponsorships_with_alarm_status, followed_sponsorships=followed_sponsorships, user=current_user)

@views.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip().lower()  # Get the search query from URL parameters and convert to lowercase

    if query:
        # Filter sponsorships by lowercased sponsor name, course, or description
        results = Sponsorship_data.query.filter(
            (Sponsorship_data.sponsor_name.ilike(f'%{query}%')) |  # Case-insensitive search for sponsor name
            (Sponsorship_data.course.ilike(f'%{query}%')) |      # Optional: search by course
            (Sponsorship_data.description.ilike(f'%{query}%'))   # Optional: search by description
            ).all()
    else:
        results = []  # Return an empty list if no query is provided

    # Return search results to the same page or to a dedicated search results page
    return render_template(
        'search_results.html',
        user=current_user,
        sponsorships=results,
        query=query  # Pass the query to display it in the search bar if needed
    )

@views.route("/profile")
@login_required
def profile():

    return render_template('profile.html', user=current_user)


from .models import Sponsorship_data  # Import your Sponsorship_data model



