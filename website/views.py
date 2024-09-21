from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Sponsorship_data
from . import db
import json
from scoring import calculate_compatibility_score

views = Blueprint('views', __name__)

@views.route('/sponsorlist', methods=['GET'])
@login_required
def recommendation():
    sponsors = Sponsorship_data.query.all()
    compatible_sponsors = [
        {
            'sponsor': sponsor,
            'score': calculate_compatibility_score(current_user, sponsor)
        }
        for sponsor in sponsors
        if calculate_compatibility_score(current_user, sponsor) >= sponsor.passing_requirement
    ]
    
    # Get followed sponsorship IDs for this user
    followed_sponsorship_ids = [sponsorship.id for sponsorship in current_user.followed_sponsorships]
    
    sponsors_with_follow_status = [
        {
            'sponsor': item['sponsor'],
            'score': item['score'],
            'is_followed': item['sponsor'].id in followed_sponsorship_ids
        }
        for item in compatible_sponsors
    ]
    
    return render_template('sponsorlist.html', user=current_user, sponsors=sponsors_with_follow_status)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # Query to get all sponsorships
    sponsorships = Sponsorship_data.query.all()
    
    # Get followed sponsorship IDs for this user
    followed_sponsorship_ids = [sponsorship.id for sponsorship in current_user.followed_sponsorships]
    
    return render_template("home.html", user=current_user, sponsorships=sponsorships, followed_sponsorship_ids=followed_sponsorship_ids)

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
