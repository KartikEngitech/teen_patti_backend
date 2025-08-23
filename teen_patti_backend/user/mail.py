import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

def mail(send_to,subject,message):
    # Email information
    sender_email = 'teenpattisupport@teen.com'
    sender_password = 'star@890#'
    receiver_email = send_to
    subject = subject
    body =  message

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Add body to email
    message.attach(MIMEText(body, 'plain'))

    # Create SMTP session
    session = smtplib.SMTP('smtpout.secureserver.net', 587)
    session.starttls()

    # Login to the sender email account
    session.login(sender_email, sender_password)

    # Send email
    text = message.as_string()
    session.sendmail(sender_email, receiver_email, text)

    # Close the SMTP session
    session.quit()


def codeverify(send_to, message):
    sender_email = 'teenpattisupport@teen.com'
    sender_password = 'star@890#'
    receiver_email = send_to
    subject = 'Hello, Welcome to Bollywood Faces! This is your verification code'
    otp = message
    
    # HTML email template with CSS styling
    email_template = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #fff;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background-color: #007bff;
                    color: #fff;
                    padding: 10px;
                    text-align: center;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                }}
                .content {{
                    padding: 20px;
                }}
                .otp {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #007bff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Hello, Welcome to Kaliper!</h2>
                </div>
                <div class="content">
                    <p>Your verification code is:</p>
                    <p class="otp">{otp}</p>
                    <p>Thank you!</p>
                </div>
            </div>
        </body>
    </html>
    """

    try:
        with smtplib.SMTP('smtpout.secureserver.net', 587) as session:
            session.starttls()
            session.login(sender_email, sender_password)

            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = receiver_email
            message['Subject'] = subject
            message.attach(MIMEText(email_template, 'html'))

            session.sendmail(sender_email, receiver_email, message.as_string())

        print('Email sent successfully.')
    except Exception as e:
        print(f'Error sending email: {str(e)}')


def generate_otp(send_to):
    try:
        sender_email = 'teenpattisupport@teen.com'
        sender_password = 'star@890#'
        receiver_email = send_to
        subject = 'Hello, Welcome to Bollywood Faces! This is your verification code'
        otp = generate_random_otp()
        message_template = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #fff;
                        border-radius: 10px;
                        padding: 20px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background-color: #007bff;
                        color: #fff;
                        padding: 10px;
                        text-align: center;
                        border-top-left-radius: 10px;
                        border-top-right-radius: 10px;
                    }}
                    .content {{
                        padding: 20px;
                    }}
                    .otp {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #007bff;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Hello, Welcome to Kaliper!</h2>
                    </div>
                    <div class="content">
                        <p>Your verification code for Kaliper is:</p>
                        <p class="otp">{otp}</p>
                        <p>Thank you!</p>
                    </div>
                </div>
            </body>
        </html>
        """

        with smtplib.SMTP('smtpout.secureserver.net', 587) as session:
            session.starttls()
            session.login(sender_email, sender_password)

            message = f"Subject: {subject}\n"
            message += "MIME-Version: 1.0\n"
            message += "Content-type: text/html\n"
            message += f"\n{message_template}"

            session.sendmail(sender_email, receiver_email, message)
        print('Email sent successfully.')
        return otp
    except Exception as e:
        print(f'Error sending email: {str(e)}')
        return None

def generate_random_otp():
    return ''.join(random.choices('0123456789', k=6))








def code_verify_for_reset_email(send_to, message):
    sender_email = 'teenpattisupport@teen.com'
    sender_password = 'star@890#'
    receiver_email = send_to
    subject = 'Hello, Welcome to Bollywood Faces! This is your Reset Email code'
    otp = message
    
    # HTML email template with CSS styling
    email_template = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #fff;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background-color: #007bff;
                    color: #fff;
                    padding: 10px;
                    text-align: center;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                }}
                .content {{
                    padding: 20px;
                }}
                .otp {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #007bff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Hello, Welcome to Kaliper!</h2>
                </div>
                <div class="content">
                    <p>Your verification code is:</p>
                    <p class="otp">{otp}</p>
                    <p>Thank you!</p>
                </div>
            </div>
        </body>
    </html>
    """

    try:
        with smtplib.SMTP('smtpout.secureserver.net', 587) as session:
            session.starttls()
            session.login(sender_email, sender_password)

            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = receiver_email
            message['Subject'] = subject
            message.attach(MIMEText(email_template, 'html'))

            session.sendmail(sender_email, receiver_email, message.as_string())

        print('Email sent successfully.')
    except Exception as e:
        print(f'Error sending email: {str(e)}')



def send_html_email(subject, to_email, reset_link):
        sender_email = settings.EMAIL_HOST_USER
        receiver_email = to_email

        # HTML email template with CSS styling
        email_template = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #fff;
                        border-radius: 10px;
                        padding: 20px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background-color: #007bff;
                        color: #fff;
                        padding: 10px;
                        text-align: center;
                        border-top-left-radius: 10px;
                        border-top-right-radius: 10px;
                    }}
                    .content {{
                        padding: 20px;
                    }}
                    .reset-link {{
                        display: block;
                        width: 100%;
                        text-align: center;
                        margin: 20px 0;
                        padding: 10px 0;
                        background-color: #007bff;
                        color: black;
                        text-decoration: none;
                        border-radius: 5px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Reset Your Password</h2>
                    </div>
                    <div class="content">
                        <p>Hello,</p>
                        <p>You can reset your password by clicking the following link:</p>
                        <a class="reset-link" href="{reset_link}">Reset Password</a>
                        <p>Thank you!</p>
                    </div>
                </div>
            </body>
        </html>
        """

        try:
            with smtplib.SMTP('smtpout.secureserver.net', 587) as session:
                session.starttls()
                session.login(sender_email, settings.EMAIL_HOST_PASSWORD)

                message = MIMEMultipart()
                message['From'] = sender_email
                message['To'] = receiver_email
                message['Subject'] = subject
                message.attach(MIMEText(email_template, 'html'))

                session.sendmail(sender_email, receiver_email, message.as_string())

            print('Email sent successfully.')
        except Exception as e:
            print(f'Error sending email: {str(e)}')