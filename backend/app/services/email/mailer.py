import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    @staticmethod
    def send_verification_email(
        recipient_email: str, 
        school_name: str, 
        code: str,
        principal_name: str = "Principal / Administrator",
        expiry_minutes: int = 5
    ) -> bool:
        """
        Sends an email with the 6-digit verification code.
        Sender: "School Portal Support" <alikhanwebdeveloper@gmail.com>
        Supports HTML + PlainText templates, standard SMTP, and local development simulation.
        """
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "alikhanwebdeveloper@gmail.com")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        smtp_from = os.getenv("SMTP_FROM", '"School Portal Support" <alikhanwebdeveloper@gmail.com>')
        support_phone = os.getenv("OWNER_PHONE", "+923215423874")

        subject = f"ExamForge AI — {code} is your School Verification Code"
        
        body_text = f"""
Hello {principal_name},

Thank you for registering {school_name} on ExamForge AI — the Multi-Tenant Bilingual Examination Generator for Khyber Pakhtunkhwa (BISEP) and Pakistani educational institutions.

Your 6-digit security verification code is:

    ================================
               {code}
    ================================

IMPORTANT: This code expires in {expiry_minutes} minutes.
Enter this code on the registration screen to activate your school account and unlock the Free Trial (2 free examination papers per subject across all Class 9th & 10th KPK Textbook Board books).

If you did not request this verification, please contact support immediately.

Support Phone (WhatsApp & SMS): {support_phone}
Official Support Email: alikhanwebdeveloper@gmail.com
Architect & Founder: Muhammad Ali (AliBuild - https://alibuild.site)
        """.strip()

        body_html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #0f172a; }}
    .container {{ max-width: 580px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
    .header {{ background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); padding: 32px 24px; text-align: center; color: #ffffff; }}
    .header h1 {{ margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; }}
    .header p {{ margin: 6px 0 0 0; font-size: 13px; opacity: 0.95; }}
    .content {{ padding: 32px 24px; }}
    .greeting {{ font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 12px; }}
    .intro {{ font-size: 14px; line-height: 1.6; color: #475569; margin-bottom: 24px; }}
    .otp-box {{ background: #fff7ed; border: 2px dashed #f97316; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0; }}
    .otp-label {{ font-size: 12px; font-weight: 700; color: #c2410c; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }}
    .otp-code {{ font-family: 'Courier New', monospace; font-size: 38px; font-weight: 900; color: #ea580c; letter-spacing: 8px; margin: 4px 0; }}
    .expiry-badge {{ display: inline-block; background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700; margin-top: 8px; }}
    .info-list {{ background: #f1f5f9; border-radius: 10px; padding: 16px; margin: 24px 0; font-size: 12px; color: #334155; }}
    .info-list p {{ margin: 6px 0; }}
    .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px 24px; text-align: center; font-size: 11px; color: #64748b; line-height: 1.6; }}
    .footer strong {{ color: #0f172a; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>ExamForge.AI</h1>
      <p>Official KPK Textbook Board (BISEP) Examination Portal</p>
    </div>
    <div class="content">
      <div class="greeting">Hello {principal_name},</div>
      <p class="intro">
        Thank you for initiating registration for <strong>{school_name}</strong> on ExamForge AI. Please use the following 6-digit verification code to confirm your institution's email address:
      </p>

      <div class="otp-box">
        <div class="otp-label">Security Verification Code</div>
        <div class="otp-code">{code}</div>
        <div class="expiry-badge">&#x23F1; Valid for {expiry_minutes} minutes only</div>
      </div>

      <div class="info-list">
        <p><strong>&#x2714; Free Trial Included:</strong> 2 Free Examination Papers per subject across all Class 9th & 10th books.</p>
        <p><strong>&#x1F512; Security Notice:</strong> Never share this OTP with anyone. ExamForge AI staff will never ask for your code.</p>
      </div>

      <p class="intro" style="margin-bottom: 0;">
        After entering this code, your school dashboard will immediately activate.
      </p>
    </div>
    <div class="footer">
      <p>
        <strong>School Portal Support:</strong> {support_phone} (WhatsApp & SMS) | <a href="mailto:alikhanwebdeveloper@gmail.com" style="color: #ea580c; text-decoration: none;">alikhanwebdeveloper@gmail.com</a><br>
        Lead Architect: <strong>Muhammad Ali (AliBuild)</strong> &bull; <a href="https://alibuild.site" style="color: #ea580c; text-decoration: none;">https://alibuild.site</a>
      </p>
    </div>
  </div>
</body>
</html>
        """.strip()

        # If SMTP is configured, attempt real email delivery
        if smtp_host and smtp_user and smtp_password:
            try:
                msg = MIMEMultipart("alternative")
                msg["From"] = smtp_from
                msg["To"] = recipient_email
                msg["Subject"] = subject
                msg.attach(MIMEText(body_text, "plain"))
                msg.attach(MIMEText(body_html, "html"))

                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
                print(f"[EMAIL DISPATCHED] Real OTP sent via SMTP to {recipient_email}")
                return True
            except Exception as e:
                print(f"[EMAIL WARNING] SMTP failed to send to {recipient_email}: {e}")

        # Local development / fallback log
        print("=" * 60)
        print(f"  [SIMULATED EMAIL DISPATCH]")
        print(f"  FROM: {smtp_from}")
        print(f"  TO: {recipient_email}")
        print(f"  SCHOOL: {school_name} (Principal: {principal_name})")
        print(f"  6-DIGIT OTP: {code}")
        print(f"  EXPIRY: {expiry_minutes} minutes")
        print("=" * 60)
        return True
