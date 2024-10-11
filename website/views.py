from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Sponsorship_data, Comment
from . import db
import json
from scoring import calculate_compatibility_score
from flask import render_template
from .utils import time_since


views = Blueprint('views', __name__)

@views.route('/sponsor/<int:sponsor_id>', methods=['GET'])
@login_required
def view_sponsorship(sponsor_id):
    print("Sponsor route hit")  # Check if this prints in the logs
    sponsor = Sponsorship_data.query.get_or_404(sponsor_id)
    is_liked = current_user in sponsor.likes

    # Fetch comments for the sponsor
    comments = Comment.query.filter_by(sponsorship_id=sponsor.id).all()
    is_following = current_user.is_following(sponsor_id)
    
    # Calculate relative time for comments
    for comment in comments:
        comment.relative_time = time_since(comment.created_at)

    return render_template('sponsor_details.html', 
                           sponsor=sponsor, 
                           comments=comments, 
                           is_liked=is_liked,
                           is_following= is_following, 
                           user=current_user)

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
    return render_template("follow.html", followed_sponsorships=followed_sponsorships, user=current_user)



@views.route("/profile")
@login_required
def profile():

    return render_template('profile.html', user=current_user)