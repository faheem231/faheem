import smtplib
import secrets
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_token():
    return secrets.token_urlsafe(32)


def send_verification_email(to_email, university_name, token, resume_id):
    actual_to = Config.TEST_EMAIL_OVERRIDE if Config.TEST_EMAIL_OVERRIDE else to_email
    verify_url = f"{Config.APP_BASE_URL}/api/confirm-verification/{token}"

    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        return {"success": False, "message": "MAIL_USERNAME or MAIL_PASSWORD missing in .env"}

    logger.info(f"[emailer] Sending to: {actual_to}")

    html_body = f"""
    <!DOCTYPE html><html><body>
    <div style="font-family:Georgia,serif;max-width:600px;margin:auto;padding:40px;
                background:#0a0a0a;color:#f5f5f3;border-radius:16px;border:1px solid rgba(212,175,55,0.25);">
        <h2 style="color:#D4AF37;letter-spacing:0.06em;text-transform:uppercase;font-family:Arial,sans-serif;">Email Verification</h2>
        <p>University: <strong>{university_name}</strong></p>
        <a href="{verify_url}"
           style="background:linear-gradient(135deg,#D4AF37,#B88A2E);color:#0a0a0a;
                  padding:14px 28px;border-radius:8px;text-decoration:none;
                  font-weight:bold;display:inline-block;margin-top:10px;">
           Verify My Email
        </a>
        <p style="margin-top:20px;font-size:12px;color:#888;">
            Valid for 24 hours. If you did not request this, ignore this email.
        </p>
    </div>
    </body></html>
    """

    plain_body = f"Verify your email:\n{verify_url}\n\nValid for 24 hours."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify Your Email - AI Resume Analyzer"
    msg["From"]    = Config.MAIL_USERNAME
    msg["To"]      = actual_to
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        # ✅ FIXED: port 465 with SMTP_SSL — works on Railway
        logger.info("[emailer] Connecting to smtp.gmail.com:465")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.ehlo()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.sendmail(Config.MAIL_USERNAME, actual_to, msg.as_string())
        logger.info(f"[emailer] Email sent successfully to {actual_to}")
        return {"success": True, "message": f"Verification email sent to {actual_to}"}

    except smtplib.SMTPAuthenticationError:
        logger.error("[emailer] Auth failed")
        return {"success": False, "message": "Auth failed - wrong App Password or MAIL_USERNAME"}

    except smtplib.SMTPConnectError:
        logger.error("[emailer] Connection failed")
        return {"success": False, "message": "Cannot connect to Gmail SMTP. Check internet."}

    except Exception as e:
        logger.error(f"[emailer] Error: {e}")
        return {"success": False, "message": str(e)}