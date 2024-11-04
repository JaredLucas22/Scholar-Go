
from website import create_app, socketio
from scoring import match_students_to_sponsorships
from website.auth import auth as auth_blueprint


app = create_app()
app.register_blueprint(auth_blueprint, url_prefix='/auth', name='auth_bp')


@app.template_filter('title_case')
def title_case(s):
    return s.title() if isinstance(s, str) else s

@app.cli.command('match')
def match():
    matches = match_students_to_sponsorships()
    for student, sponsor, score in matches:
        print(f"Student {student.first_name} matched with Sponsor {sponsor.sponsor_name} with a score of {score}")

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

