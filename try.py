import smtplib
from email.mime.text import MIMEText
from flask import Flask, request

app = Flask(__name__)

@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        # Get email details from the form
        sender_email = 'pearlmeht@gmail.com'  # Replace with your email address
        recipient_email = request.form['email']
        subject = 'Appointment Confirmation'
        message = 'Your appointment has been confirmed.'

        # Create a MIMEText object
        email_message = MIMEText(message)
        email_message['Subject'] = subject
        email_message['From'] = sender_email
        email_message['To'] = recipient_email

        # Connect to the SMTP server and send the email
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, 'your_password')  # Replace with your email password
                server.sendmail(sender_email, recipient_email, email_message.as_string())
                return 'Email sent successfully!'
        except Exception as e:
            return str(e)

if __name__ == '__main__':
    app.run(debug=True)
