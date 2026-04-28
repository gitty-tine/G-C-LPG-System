import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


GMAIL_ADDRESS      = "gnclpgsystem@gmail.com"
GMAIL_APP_PASSWORD = "heyz ofmo jmdi qrjb"
DISPLAY_NAME       = "G&C System No Reply"


def send_reset_code(to_email, code, full_name=""):
    subject = "G&C LPG Trading — Password Reset Code"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background: #f4f5f4; padding: 32px;">
        <div style="max-width: 480px; margin: auto; background: #ffffff;
                    border-radius: 10px; padding: 32px; border: 1px solid #e6eae9;">
            <h2 style="color: #1A7A6E; margin-bottom: 4px;">G and C LPG Trading</h2>
            <p style="color: #7a8a87; font-size: 13px; margin-top: 0;">
                Delivery Scheduling & Tracking System
            </p>
            <hr style="border: none; border-top: 1px solid #e6eae9; margin: 20px 0;">
            <p style="color: #3a4a47; font-size: 15px;">
                Hi <strong>{full_name or "there"}</strong>,
            </p>
            <p style="color: #3a4a47; font-size: 14px;">
                We received a request to reset your password.
                Use the code below to proceed:
            </p>
            <div style="text-align: center; margin: 28px 0;">
                <span style="font-size: 36px; font-weight: bold;
                             letter-spacing: 10px; color: #1A7A6E;">
                    {code}
                </span>
            </div>
            <p style="color: #7a8a87; font-size: 13px;">
                This code expires in <strong>10 minutes</strong>.
                If you did not request a password reset, you can ignore this email.
            </p>
            <hr style="border: none; border-top: 1px solid #e6eae9; margin: 20px 0;">
            <p style="color: #c4ccc9; font-size: 11px; text-align: center;">
                © 2026 G and C LPG Trading. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{DISPLAY_NAME} <{GMAIL_ADDRESS}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
