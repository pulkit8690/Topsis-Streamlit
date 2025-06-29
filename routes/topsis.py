from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from services.topsis_service import calculate_custom_score, load_input_data, validate_numeric_values, validate_weights_impacts
from utils.validators import validate_email
from services.email_service import send_email

topsis_bp = Blueprint('topsis', __name__)

@topsis_bp.route('/submit', methods=['POST'])
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

@topsis_bp.route('/process', methods=['POST'])
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