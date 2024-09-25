from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Sponsorship_data
from . import db
import json
from scoring import calculate_compatibility_score

views = Blueprint('views', __name__)

@views.route('/sponsorship/<int:sponsorship_id>', methods=['GET'])
@login_required
def get_sponsorship(sponsorship_id):
    # Fetch the sponsorship data by ID
    sponsorship = Sponsorship_data.query.get_or_404(sponsorship_id)
    
    # Return sponsorship details as JSON
    return jsonify({
        'sponsor_name': sponsorship.sponsor_name,
        'passing_requirement': sponsorship.passing_requirement,
        'description': sponsorship.description,
        'full_description': sponsorship.full_description,
        'likes': sponsorship.likes,
        'deadline_date': sponsorship.deadline_date.strftime('%B %d, %Y'),
        'course': sponsorship.course,
        'amount_per_semester': sponsorship.amount_per_semester
    })


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

@views.route('/my_bookmarks')
@login_required
def my_bookmarks():
    # Fetch followed sponsorships
    bookmarks = current_user.followed_sponsorships
    return render_template('follow.html', bookmarks=bookmarks)
