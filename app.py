import pandas as pd
import numpy as np
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st

# Function to validate email format
# Function to validate email format
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email.strip())


# Define function to load input data
def load_input_data(input_file):
    try:
        data = pd.read_csv(input_file)
        return data
    except FileNotFoundError:
        return None

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
    weighted_normalized_data = normalized_data * list(map(float, weights.split(',')))  # Convert weights to float
    ideal_best = weighted_normalized_data.max() if impacts[0] == '+' else weighted_normalized_data.min()
    ideal_worst = weighted_normalized_data.min() if impacts[0] == '+' else weighted_normalized_data.max()
    custom_score = np.sqrt(np.sum((weighted_normalized_data - ideal_best)**2, axis=1)) / (
            np.sqrt(np.sum((weighted_normalized_data - ideal_best)**2, axis=1)) +
            np.sqrt(np.sum((weighted_normalized_data - ideal_worst)**2, axis=1))
    )
    return custom_score


# Define function to send email with result CSV attached
def send_email(data, weights, impacts, recipient_email):
    # Email configuration
    sender_email = '2003pulkit@gmail.com'  # Update with your email address
    password = 'rkiq uskn hvsm wuok'  # Update with your email password
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
    attachment.set_payload(result_csv)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename='result_with_rank.csv')
    msg.attach(attachment)

    # Connect to Gmail server and send email
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()

# Main Streamlit app
def main():
    st.title("TOPSIS Analysis")

    # Input fields
    uploaded_file = st.file_uploader("Upload a CSV file")
    if uploaded_file:
        weights = st.text_input("Weights (comma-separated)")
        impacts = st.text_input("Impacts (comma-separated, '+' or '-')")
        email = st.text_input("Your Email")

        if st.button("Submit"):
            # Check email format
            if not validate_email(email):
                st.error("Please enter a valid email address.")
                return

            # Load data
            data = pd.read_csv(uploaded_file)

            # Validation
            if not weights:
                st.error("Please provide weights.")
            elif not impacts:
                st.error("Please provide impacts.")
            elif not validate_numeric_values(data):
                st.error("Columns from 2nd to last must contain numeric values only.")
            elif not validate_weights_impacts(weights, impacts, len(data.columns)):
                st.error("Invalid weights or impacts.")
            else:
                # Calculation
                custom_score = calculate_custom_score(data, weights, impacts)

                # Add custom score to data
                data['Custom Score'] = custom_score

                # Send email with result CSV attached
                send_email(data, weights, impacts, email)

                # Confirmation message
                st.success("Result has been sent to your email address.")

    # Footer
    st.markdown("""
        <div class="made-by">
            Made by Pulkit Arora (102103267) <br>
            <a href="https://www.linkedin.com/in/pulkit-arora-731b17227/" target="_blank">LinkedIn</a> | 
            <a href="https://github.com/pulkit8690" target="_blank">Github</a>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
