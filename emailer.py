import secrets
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_token():
    return secrets.token_urlsafe(32)


def send_verification_email(to_email, university_name, token, resume_id):
    actual_to  = Config.TEST_EMAIL_OVERRIDE if Config.TEST_EMAIL_OVERRIDE else to_email
    verify_url = f"{Config.APP_BASE_URL}/api/confirm-verification/{token}"

    if not Config.SENDGRID_API_KEY:
        return {"success": False, "message": "SENDGRID_API_KEY missing in environment variables"}

    html_body = f"""
    <!DOCTYPE html><html><body>
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:40px;
                background:#0a0a0a;color:#f5f5f3;border-radius:16px;">
        <h2 style="color:#7C3AED;">Email Verification</h2>
        <p>University: <strong>{university_name}</strong></p>
        <a href="{verify_url}"
           style="background:linear-gradient(135deg,#7C3AED,#2563EB);color:#fff;
                  padding:14px 28px;border-radius:8px;text-decoration:none;
                  font-weight:bold;display:inline-block;margin-top:10px;">
           Verify My Email
        </a>
        <p style="margin-top:20px;font-size:12px;color:#888;">
            Valid for 24 hours.
        </p>
    </div>
    </body></html>
    """

    try:
        message = Mail(
            from_email = Config.MAIL_USERNAME,
            to_emails  = actual_to,
            subject    = "Verify Your Email - AI Resume Analyzer",
            html_content = html_body
        )
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"[emailer] Sent! Status: {response.status_code}")
        return {"success": True, "message": f"Verification email sent to {actual_to}"}

    except Exception as e:
        logger.error(f"[emailer] Error: {e}")
        return {"success": False, "message": str(e)}