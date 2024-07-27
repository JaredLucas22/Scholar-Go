from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Sponsorship_data
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


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
        course = request.form.get('course')
        gpa  = request.form.get('gpa')
        extracurricular_activities = request.form.get('extracurricularActivities')
        financial_status = request.form.get('financialStatus')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

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
            new_user = User(
                email=email,
                first_name=first_name,
                course = course,
                password=generate_password_hash(password1, method='pbkdf2:sha256'),
                gpa=gpa,
                extracurricular_activities=extracurricular_activities,
                financial_status = financial_status)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/sign-sponsor', methods=['GET', 'POST'])
def sign_sponsor():
    if request.method == 'POST':
        sponsor_name = request.form.get('sponsor-name')
        course = request.form.get('course')
        weight_fos = float(request.form.get('weight_fos'))
        weight_gpa = float(request.form.get('weightgpa'))
        weight_extracurricular = float(request.form.get('weightextracurricularActivities'))
        weight_financial = float(request.form.get('weightfinancialStatus'))
        passing_requirement = float(request.form.get('passingrequirement'))

        if weight_fos + weight_gpa + weight_extracurricular + weight_financial != 1:
            flash('The total weight of FOS, GPA, extracurricular activities, and financial status must be equal to 1.')
            return redirect(url_for('sponsor'))

        new_sponsor = Sponsorship_data(
            sponsor_name=sponsor_name,
            course=course,
            weight_fos=weight_fos,
            weight_gpa=weight_gpa,
            weight_extracurricular_activities=weight_extracurricular,
            weight_financial_status=weight_financial,
            passing_requirement=passing_requirement
        )
        db.session.add(new_sponsor)
        db.session.commit()

        flash('Sponsor added successfully!')
        return redirect(url_for('auth.login'))

    return render_template("sign_sponsor.html",  user=current_user)