from website import create_app, db
from website.models import User, Sponsorship_data

# Define scoring functions for each criterion
def score_academic_performance(gpa, weight):
    score = min(gpa * 25 * weight, 100)  # Convert GPA to a score out of 100, weighted
    return score

def score_financial_need(financial_status, weight):
    financial_mapping = {
        'Low Income': 100,
        'Lower Middle': 75,
        'Middle': 50,
        'Upper Middle': 25,
        'Rich': 0
    }
    base_score = financial_mapping.get(financial_status, 0)
    score = base_score * weight
    return score

def score_extracurricular(activities, weight):
    score = min(len(activities.split(',')) * 10 * weight, 100)  # Each activity worth 10 points, weighted
    return score

def score_course(student_course, sponsor_course, weight):
    score = 100 * weight if student_course == sponsor_course else 0
    return score

# Calculate overall compatibility score for an applicant based on sponsorship criteria
def calculate_compatibility_score(applicant, sponsor):
    weight_fos = safe_float(sponsor.weight_fos)
    weight_gpa = safe_float(sponsor.weight_gpa)
    weight_extracurricular_activities = safe_float(sponsor.weight_extracurricular_activities)
    weight_financial_status = safe_float(sponsor.weight_financial_status)

    scores = {
        'academic_performance': score_academic_performance(applicant.gpa, weight_gpa),
        'financial_need': score_financial_need(applicant.financial_status, weight_financial_status),
        'extracurricular_activities': score_extracurricular(applicant.extracurricular_activities, weight_extracurricular_activities),
        'course': score_course(applicant.course, sponsor.course, weight_fos)
    }

    overall_score = sum(scores.values())
    capped_score = min(overall_score, 100)
    
    return capped_score

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0  # Default to 0 if conversion fails
def match_students_to_sponsorships():
    app = create_app()
    with app.app_context():
        print("Debug: App context entered.")
        
        students = User.query.all()
        sponsors = Sponsorship_data.query.all()
        
        print(f"Debug: Number of students retrieved: {len(students)}")
        print(f"Debug: Number of sponsors retrieved: {len(sponsors)}")
        
        matches = []

        for student in students:
            print(f"Debug: Evaluating Student {student.first_name}")
            for sponsor in sponsors:
                print(f"Debug: Evaluating Sponsor {sponsor.sponsor_name}")
                score = calculate_compatibility_score(student, sponsor)
                passing_requirement = safe_float(sponsor.passing_requirement)
                if score >= passing_requirement:
                    print(f"Debug: Match found - Student {student.first_name} with Sponsor {sponsor.sponsor_name} (Score: {score})")
                    matches.append((student, sponsor, score))
                else:
                    print(f"Debug: No match - Student {student.first_name} with Sponsor {sponsor.sponsor_name} (Score: {score})")

        print(f"Debug: Total matches found: {len(matches)}")
        return matches

if __name__ == "__main__":
    print("Debug: Starting script.")
    matches = match_students_to_sponsorships()
    for student, sponsor, score in matches:
        print(f"Student {student.first_name} matched with Sponsor {sponsor.sponsor_name} with a score of {score}")
