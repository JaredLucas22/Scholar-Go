import logging
from website import create_app, db
from website.models import User, Sponsorship_data

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define scoring functions for each criterion
def score_academic_performance(gpa, weight):
    score = min(gpa * 25 * weight, 100)
    logger.debug(f"Academic Performance Score: {score} (GPA: {gpa}, Weight: {weight})")
    return score

def score_financial_need(financial_status, weight):
    financial_mapping = {
        'Self-Funded': 100,
        'Low Income': 75,
        'Middle Income': 50,
        'High Income': 25,
    }
    base_score = financial_mapping.get(financial_status, 0)
    score = base_score * weight
    logger.debug(f"Financial Need Score: {score} (Status: {financial_status}, Weight: {weight})")
    return score

def score_extracurricular(activities, weight):
    score = min(len(activities.split(',')) * 10 * weight, 100)
    logger.debug(f"Extracurricular Score: {score} (Activities: {activities}, Weight: {weight})")
    return score

def score_course(student_educationlevel, sponsor_course, weight, course_range):
    # Logging the received values for troubleshooting
    logger.info(f"Calculating score for: student_educationlevel='{student_educationlevel}', sponsor_course='{sponsor_course}', "
                f"weight={weight}, course_range='{course_range}'")
    
    # Normalize course names
    student_educationlevel = student_educationlevel.lower().strip()
    sponsor_course = sponsor_course.lower().strip()

    # Initialize score and feedback
    score = 0
    feedback = ""

    # Scoring logic based on course ranges
    if course_range == "pre school to college":
        if student_educationlevel in ["pre school", "elementary", "junior high", "senior high", "college"]:
            if student_educationlevel == sponsor_course:
                score = 100 * weight
                feedback = "Exact match in the pre-school to college range."
            elif student_educationlevel in sponsor_course or sponsor_course in student_educationlevel:
                score = 50 * weight
                feedback = "Partial match in the pre-school to college range."
            else:
                feedback = "No match in the pre-school to college range."

    # Additional range checks omitted for brevity (keep existing logic)

    # Log the result
    logging.info(f"Score calculated: {score}, Feedback: {feedback}")
    return score, feedback

def score_fieldofstudy(student_course, sponsor_fos, weight):
    score = 100 * weight if student_course == sponsor_fos else 0
    logger.debug(f"Field of Study Score: {score} (Student Field: {student_course}, Sponsor Field: {sponsor_fos}, Weight: {weight})")
    return score

def score_location(student_city, student_province, student_postalcode, sponsor, weight):
    # Initialize the score to 0
    score = 0

    # Check for None values and normalize to lowercase
    student_city = student_city.lower().strip() if student_city else ""
    student_province = student_province.lower().strip() if student_province else ""
    student_postalcode = student_postalcode.strip() if student_postalcode else ""
    
    tar_city = sponsor.tar_city.lower().strip() if sponsor.tar_city else ""
    tar_province = sponsor.tar_province.lower().strip() if sponsor.tar_province else ""
    tar_postalcode = sponsor.tar_postalcode.strip() if sponsor.tar_postalcode else ""

    logger.debug(f"Comparing - Student: (City: '{student_city}', Province: '{student_province}', Postal Code: '{student_postalcode}') "
                 f"with Sponsor: (City: '{tar_city}', Province: '{tar_province}', Postal Code: '{tar_postalcode}')")

    # Full match for city, province, and postal code
    if (student_city == tar_city and student_province == tar_province and student_postalcode == tar_postalcode) or \
       (student_city == tar_province and student_province == tar_city and student_postalcode == tar_postalcode):
        score = 100 * weight
        logger.debug("Full location match achieved.")
    # Partial match for city or province
    elif (student_city == tar_city or student_province == tar_province or 
          student_city == tar_province or student_province == tar_city):
        score = 50 * weight
        logger.debug("Partial location match achieved.")
    else:
        logger.debug("No location match.")

    # Log detailed information
    logger.debug(
        f"Location Score: {score} "
        f"(Student City: '{student_city}', Student Province: '{student_province}', "
        f"Student Postal Code: '{student_postalcode}', Target City: '{tar_city}', "
        f"Target Province: '{tar_province}', Target Postal Code: '{tar_postalcode}', Weight: {weight})"
    )

    return score

def calculate_compatibility_score(applicant, sponsor):
    weight_fos = safe_float(sponsor.weight_fos)
    weight_course = safe_float(sponsor.weight_course)
    weight_gpa = safe_float(sponsor.weight_gpa)
    weight_extracurricular_activities = safe_float(sponsor.weight_extracurricular_activities)
    weight_financial_status = safe_float(sponsor.weight_financial_status)
    weight_loc = safe_float(sponsor.weight_loc)

    # Use educationlevel from applicant instead of course attribute
    scores = {
        'academic_performance': score_academic_performance(applicant.gpa, weight_gpa),
        'financial_need': score_financial_need(applicant.financial_status, weight_financial_status),
        'extracurricular_activities': score_extracurricular(applicant.extracurricular_activities, weight_extracurricular_activities),
        'course': score_course(applicant.educationlevel, sponsor.course, weight_course, sponsor.course)[0],
        'field_of_study': score_fieldofstudy(applicant.course, sponsor.fos, weight_fos),
        'location': score_location(applicant.city, applicant.province, applicant.postalcode, sponsor, weight_loc)
    }

    total_score = sum(scores.values())
    logger.debug(f"Total Compatibility Score for {applicant.first_name} with Sponsor {sponsor.sponsor_name}: {total_score}")
    return total_score

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Invalid value for conversion to float: {value}")
        return 0

def match_students_to_sponsorships():
    app = create_app()
    with app.app_context():
        logger.info("App context entered.")
        students = User.query.all()
        sponsors = Sponsorship_data.query.all()

        logger.info(f"Number of students retrieved: {len(students)}")
        logger.info(f"Number of sponsors retrieved: {len(sponsors)}")

        matches = []

        for student in students:
            logger.info(f"Evaluating Student {student.first_name}")
            for sponsor in sponsors:
                score = calculate_compatibility_score(student, sponsor)
                passing_requirement = safe_float(sponsor.passing_requirement)

                logger.debug(f"Score for {student.first_name} with Sponsor {sponsor.sponsor_name}: {score}, Passing Requirement: {passing_requirement}")
                
                if score >= passing_requirement:
                    logger.info(f"Match found - Student {student.first_name} with Sponsor {sponsor.sponsor_name} (Score: {score})")
                    matches.append((student, sponsor, score))
                else:
                    logger.info(f"No match - Student {student.first_name} with Sponsor {sponsor.sponsor_name} (Score: {score})")

        logger.info(f"Total matches found: {len(matches)}")
        return matches, len(matches), len(students)

if __name__ == "__main__":
    logger.info("Starting match_students_to_sponsorships script.")
    matches, matched_count, total_students = match_students_to_sponsorships()
    
    if matched_count > 0:
        for student, sponsor, score in matches:
            logger.info(f"Student {student.first_name} matched with Sponsor {sponsor.sponsor_name} with a score of {score}")
    else:
        logger.info("No matches found.")
