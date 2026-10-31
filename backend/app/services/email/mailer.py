import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    @staticmethod
    def send_verification_email(recipient_email: str, school_name: str, code: str) -> bool:
        """
        Sends an email with the 6-digit verification code.
        Supports standard SMTP or logs to console when running in local development mode.
        """
        smtp_host = os.getenv("SMTP_HOST", "")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        smtp_from = os.getenv("SMTP_FROM", "noreply@examforge.ai")

        subject = f"ExamForge AI — Verification Code for {school_name}"
        body_text = f"""
Hello Administrator,

Thank you for registering {school_name} on ExamForge AI — the Multi-Tenant Bilingual Examination Generator for Khyber Pakhtunkhwa (BISEP) and Pakistani boards.

Your 6-digit email verification code is:

    ======================
        {code}
    ======================

This code is valid for 30 minutes. Enter this code on the registration page to activate your school account.

Upon verification, your school account will have full access to our Free Trial (2 free examination papers per subject across all Class 9th and 10th KPK Textbook Board books).

Regards,
ExamForge AI Team
Lead Architect: Muhammad Ali (alibuild.site)
        """.strip()

        # If SMTP is configured, attempt real email delivery
        if smtp_host and smtp_user and smtp_password:
            try:
                msg = MIMEMultipart()
                msg["From"] = smtp_from
                msg["To"] = recipient_email
                msg["Subject"] = subject
                msg.attach(MIMEText(body_text, "plain"))

                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
                print(f"[EMAIL DISPATCHED] Verification code sent via SMTP to {recipient_email}")
                return True
            except Exception as e:
                print(f"[EMAIL WARNING] SMTP failed to send to {recipient_email}: {e}")

        # Local development / fallback log
        print("=" * 60)
        print(f"  [SIMULATED EMAIL DISPATCH] TO: {recipient_email}")
        print(f"  SCHOOL: {school_name}")
        print(f"  VERIFICATION CODE: {code}")
        print("=" * 60)
        return True
