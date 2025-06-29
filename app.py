import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.io as pio
import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from werkzeug.utils import secure_filename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://db_user:db_pass@localhost:5432/db_name'
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    otp = db.Column(db.String(6), nullable=True)
    otp_valid = db.Column(db.Boolean, default=False)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dataset_info = db.Column(db.Text, nullable=True)
    result = db.Column(db.Text, nullable=True)

# Create tables once in a separate script or in main()
# db.create_all()

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash("Email already in use.")
            return redirect(url_for('signup'))
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Signup successful.")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            # Generate OTP
            user.otp = str(random.randint(100000, 999999))
            user.otp_valid = True
            db.session.commit()
            # Send OTP by email
            send_otp_email(email, user.otp)
            flash("OTP sent. Please verify.")
            return redirect(url_for('verify_otp'))
        flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/verify_otp', methods=['GET','POST'])
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

# Example: Storing history after processing
def process_dataset(data):
    # ... existing code to process dataset and get result ...
    # Store in history if user is logged in
    if 'user_id' in session:
        history = History(user_id=session['user_id'],
                          dataset_info="Sample dataset info",
                          result=data.to_csv(index=False))
        db.session.add(history)
        db.session.commit()

def send_otp_email(email, otp):
    # Simple example to send OTP using smtplib
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.getenv("SENDER_EMAIL"), os.getenv("EMAIL_PASSWORD"))
        message = f"Subject: Your OTP Code\n\nYour OTP is: {otp}"
        server.sendmail(os.getenv("SENDER_EMAIL"), email, message)
        server.quit()
    except Exception as e:
        print("Error sending OTP:", str(e))

# Function to validate email format
def validate_email(email):
    if not email:
        return True  # If email is empty, allow it
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email.strip())

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define function to load input data
def load_input_data(input_file):
    if input_file.endswith('.csv'):
        data = pd.read_csv(input_file)
    elif input_file.endswith('.xlsx'):
        data = pd.read_excel(input_file)
    else:
        return None
    return data

# Define function to validate numeric values
def validate_numeric_values(data):
    non_numeric_columns = data.iloc[:, 1:].applymap(lambda x: not np.isreal(x)).any()
    return not non_numeric_columns.any()

# Define function to validate weights and impacts
def validate_weights_impacts(weights, impacts, num_columns):
    try:
        weights_list = list(map(float, weights.split(',')))
    except ValueError:
        return False

    impacts_list = impacts.split(',')

    if len(weights_list) != num_columns - 1 or len(impacts_list) != num_columns - 1:
        return False

    if not all(impact in ['+', '-'] for impact in impacts_list):
        return False

    return True

# Define function to calculate custom score
def calculate_custom_score(data, weights, impacts):
    normalized_data = data.iloc[:, 1:].apply(lambda x: x / np.sqrt(np.sum(x**2)), axis=0)
    weighted_normalized_data = normalized_data * list(map(float, weights.split(',')))
    ideal_best = weighted_normalized_data.max() if impacts[0] == '+' else weighted_normalized_data.min()
    ideal_worst = weighted_normalized_data.min() if impacts[0] == '+' else weighted_normalized_data.max()
    custom_score = np.sqrt(np.sum((weighted_normalized_data - ideal_best)**2, axis=1)) / (
            np.sqrt(np.sum((weighted_normalized_data - ideal_best)**2, axis=1)) +
            np.sqrt(np.sum((weighted_normalized_data - ideal_worst)**2, axis=1))
    )
    return custom_score

# Function to send email with result attachment using SMTP
def send_email(data, recipient_email):
    if not recipient_email:  # Skip sending email if no email is provided
        return

    # Access the variables
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    subject = os.getenv("EMAIL_SUBJECT")

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Email body
    body = "Dear User,\n\nAttached is the TOPSIS result CSV file you requested.\n\nBest regards,\nPulkit Arora"
    msg.attach(MIMEText(body, 'plain'))

    # Attach result CSV file
    data_with_rank = data.copy()
    data_with_rank['Rank'] = data['Custom Score'].rank(ascending=False)
    result_csv = data_with_rank.to_csv(index=False)
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(result_csv.encode('utf-8'))
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename='result_with_rank.csv')
    msg.attach(attachment)

    # Connect to Gmail server and send email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        flash('Result has been sent to your email address.')
    except Exception as e:
        flash(f'Failed to send email: {str(e)}')

# Main Flask app
def main():
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/submit', methods=['POST'])
    def submit():
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('index'))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('index'))
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a CSV or XLSX file.')
            return redirect(url_for('index'))

        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Load data
        data = load_input_data(file_path)
        if data is None:
            flash('File not found or invalid.')
            return redirect(url_for('index'))

        # Render column names for weights and impacts input
        columns = data.columns[1:]  # Exclude the first column (e.g., item names)
        
        # Save filename to session
        session['uploaded_file'] = filename

        return render_template('weights_impacts.html', columns=columns)

    @app.route('/process', methods=['POST'])
    def process():
        weights = request.form.getlist('weights')
        impacts = request.form.getlist('impacts')
        email = request.form.get('email', None)  
        filename = session.get('uploaded_file')  

        if not filename:
            flash('No file uploaded. Please upload a file first.')
            return redirect(url_for('index'))

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Validate email only if provided and not empty
        if email and email.strip():
            if not validate_email(email):
                flash('Invalid email format.')
                return redirect(url_for('index'))


        # Load data
        try:
            data = load_input_data(file_path)
        except FileNotFoundError:
            flash('File not found. Please upload the dataset again.')
            return redirect(url_for('index'))

        # Validate weights and impacts
        if not weights or not impacts:
            flash('Please provide weights and impacts.')
            return redirect(url_for('index'))
        if not validate_numeric_values(data):
            flash('Columns from 2nd to last must contain numeric values only.')
            return redirect(url_for('index'))
        if len(data.columns) - 1 != len(weights) or len(data.columns) - 1 != len(impacts):
            flash('The number of weights and impacts must match the dataset criteria.')
            return redirect(url_for('index'))
        if not validate_weights_impacts(','.join(weights), ','.join(impacts), len(data.columns)):
            flash('Invalid weights or impacts.')
            return redirect(url_for('index'))

        # Calculate custom score
        custom_score = calculate_custom_score(data, ','.join(weights), ','.join(impacts))

        # Add custom score to data
        data['Custom Score'] = custom_score
        data['Rank'] = data['Custom Score'].rank(ascending=False)

        # Visualize results
        fig = px.bar(data, x=data.columns[0], y='Custom Score', title='TOPSIS Scores by Alternative', text='Rank')
        graph_html = pio.to_html(fig, full_html=False)

        # Save results to CSV
        result_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_with_rank.csv')
        data.to_csv(result_csv_path, index=False)

        # Send email only if an email is provided
        send_email(data, email)

        return render_template('result.html', graph_html=graph_html, csv_download_link='/download')

    @app.route('/download', methods=['GET'])
    def download():
        result_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_with_rank.csv')
        return send_file(result_csv_path, as_attachment=True)

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if __name__ == "__main__":
        app.run(debug=True)

main()
