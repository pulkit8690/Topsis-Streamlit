from flask import flash
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_otp_email(email, otp):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.getenv("SENDER_EMAIL"), os.getenv("EMAIL_PASSWORD"))
        message = f"Subject: Your OTP Code\n\nYour OTP is: {otp}"
        server.sendmail(os.getenv("SENDER_EMAIL"), email, message)
        server.quit()
    except Exception as e:
        print("Error sending OTP:", str(e))

def send_email(data, recipient_email):
    if not recipient_email:
        return

    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    subject = os.getenv("EMAIL_SUBJECT")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    body = "Dear User,\n\nAttached is the TOPSIS result CSV file you requested.\n\nBest regards,\nPulkit Arora"
    msg.attach(MIMEText(body, 'plain'))

    data_with_rank = data.copy()
    data_with_rank['Rank'] = data['Custom Score'].rank(ascending=False)
    result_csv = data_with_rank.to_csv(index=False)
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(result_csv.encode('utf-8'))
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename='result_with_rank.csv')
    msg.attach(attachment)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        flash('Result has been sent to your email address.')
    except Exception as e:
        flash(f'Failed to send email: {str(e)}')