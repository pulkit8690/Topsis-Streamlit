import pandas as pd
import numpy as np
import re
import os
import plotly.express as px
import plotly.io as pio
import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
# import dotenv

# # Load environment variables from dot.env file
# dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to validate email format
def validate_email(email):
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
    if non_numeric_columns.any():
        return False
    return True

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
# Function to send email with result attachment using SMTP
def send_email(data, weights, impacts, recipient_email):
    # Email configuration
    sender_email = '2003pulkit@gmail.com'  # Update with your email address
    password = 'yhme lbzn zpgw fppo'  # Ensure this is set to your App Password
    subject = 'TOPSIS Result'

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Email body
    body = f"Dear User,\n\nAttached is the TOPSIS result CSV file you requested.\n\nBest regards,\nPulkit Arora\n\nLinkedIn: https://www.linkedin.com/in/pulkit-arora-731b17227/"
    msg.attach(MIMEText(body, 'plain'))

    # Attach result CSV file with rank included
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
        if request.method == 'POST':
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
            
            # Save filename to be used later
            session['uploaded_file'] = filename

            return render_template('weights_impacts.html', columns=columns)

    @app.route('/process', methods=['POST'])
    def process():
        if request.method == 'POST':
            # Retrieve form data
            weights = request.form.getlist('weights')
            impacts = request.form.getlist('impacts')
            email = request.form['email']
            filename = session.get('uploaded_file')  # Retrieve saved filename

            if not filename:
                flash('No file uploaded. Please upload a file first.')
                return redirect(url_for('index'))

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Validate email
            if not validate_email(email):
                flash('Please enter a valid email address.')
                return redirect(url_for('index'))

            # Load data
            try:
                data = load_input_data(file_path)
            except FileNotFoundError:
                flash('File not found. Please upload the dataset again.')
                return redirect(url_for('index'))

            # Validate weights and impacts
            if not weights:
                flash('Please provide weights.')
                return redirect(url_for('index'))
            if not impacts:
                flash('Please provide impacts.')
                return redirect(url_for('index'))
            if not validate_numeric_values(data):
                flash('Columns from 2nd to last must contain numeric values only.')
                return redirect(url_for('index'))
            if len(data.columns) - 1 != len(weights) or len(data.columns) - 1 != len(impacts):
                flash('The number of weights and impacts must match the number of criteria in the dataset.')
                return redirect(url_for('index'))
            if not validate_weights_impacts(','.join(weights), ','.join(impacts), len(data.columns)):
                flash('Invalid weights or impacts.')
                return redirect(url_for('index'))

            # Calculate custom score
            custom_score = calculate_custom_score(data, ','.join(weights), ','.join(impacts))

            # Add custom score to data
            data['Custom Score'] = custom_score
            data['Rank'] = data['Custom Score'].rank(ascending=False)

            # Visualize results using Plotly
            fig = px.bar(data, x='Fund Name', y='Custom Score', title='TOPSIS Scores by Alternative', text='Rank')
            graph_html = pio.to_html(fig, full_html=False)

            # Save results to CSV
            result_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_with_rank.csv')
            data.to_csv(result_csv_path, index=False)

            # Send email with result CSV attached
            send_email(data, ','.join(weights), ','.join(impacts), email)

            # Render results page with interactive chart
            return render_template('result.html', graph_html=graph_html, csv_download_link='/download')
        else:
            flash('Invalid request method. Please submit the form using POST.')
            return redirect(url_for('index'))

    @app.route('/download', methods=['GET'])
    def download():
        result_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_with_rank.csv')
        return send_file(result_csv_path, as_attachment=True)

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if __name__ == "__main__":
        app.run(debug=True)

main()
