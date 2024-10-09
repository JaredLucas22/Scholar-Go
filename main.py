
from website import create_app, socketio
from scoring import match_students_to_sponsorships


app = create_app()

@app.cli.command('match')
def match():
    matches = match_students_to_sponsorships()
    for student, sponsor, score in matches:
        print(f"Student {student.first_name} matched with Sponsor {sponsor.sponsor_name} with a score of {score}")

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

