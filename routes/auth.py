from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from services.email_service import send_otp_email
from app import db
import random

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash("Email already in use.")
            return redirect(url_for('auth.signup'))
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Signup successful.")
        return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            user.otp = str(random.randint(100000, 999999))
            user.otp_valid = True
            db.session.commit()
            send_otp_email(email, user.otp)
            flash("OTP sent. Please verify.")
            return redirect(url_for('auth.verify_otp'))
        flash("Invalid credentials.")
    return render_template('login.html')

@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        email = request.form['email']
        otp_submitted = request.form['otp']
        user = User.query.filter_by(email=email).first()
        if user and user.otp_valid and user.otp == otp_submitted:
            user.otp_valid = False
            db.session.commit()
            session['user_id'] = user.id
            flash("Login successful.")
            return redirect(url_for('index'))
        flash("Invalid OTP.")
    return render_template('verify_otp.html')