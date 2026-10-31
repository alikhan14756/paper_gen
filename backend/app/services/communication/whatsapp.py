import os
import re
import httpx

class WhatsAppService:
    @staticmethod
    def format_pakistan_phone(phone: str) -> str:
        """
        Normalizes Pakistani phone numbers to standard international format (+923XXXXXXXXX).
        Accepts: 03215423874, 923215423874, +923215423874, 0321-5423874, etc.
        """
        cleaned = re.sub(r"[^\d+]", "", phone.strip())
        if cleaned.startswith("+92"):
            return cleaned
        if cleaned.startswith("92"):
            return f"+{cleaned}"
        if cleaned.startswith("03"):
            return f"+92{cleaned[1:]}"
        if cleaned.startswith("3"):
            return f"+92{cleaned}"
        return cleaned

    @classmethod
    def send_verification_whatsapp(
        cls,
        recipient_phone: str,
        school_name: str,
        code: str,
        principal_name: str = "Principal / Administrator",
        expiry_minutes: int = 5
    ) -> bool:
        """
        Dispatches a WhatsApp verification message to the principal's mobile number.
        Sender/Support phone: +923215423874.
        Supports Meta WhatsApp Cloud API, Twilio WhatsApp API, and simulated dev logging.
        """
        normalized_phone = cls.format_pakistan_phone(recipient_phone)
        sender_phone = os.getenv("OWNER_PHONE", "+923215423874")
        
        message_body = (
            f"🔐 *ExamForge AI — School Verification Code*\n\n"
            f"Hello *{principal_name}*,\n"
            f"Your 6-digit security code for *{school_name}* is:\n\n"
            f"👉 *{code}*\n\n"
            f"⏱ Valid for *{expiry_minutes} minutes*.\n"
            f"🎁 Free Trial: 2 Free Examination Papers per subject across all Class 9th & 10th KPK Textbooks.\n\n"
            f"Support: {sender_phone} | alikhanwebdeveloper@gmail.com\n"
            f"Founder: Muhammad Ali (AliBuild - https://alibuild.site)"
        )

        # 1. Attempt Meta WhatsApp Business Cloud API
        whatsapp_token = os.getenv("WHATSAPP_TOKEN", "")
        phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        if whatsapp_token and phone_number_id:
            try:
                url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
                headers = {
                    "Authorization": f"Bearer {whatsapp_token}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": normalized_phone.replace("+", ""),
                    "type": "text",
                    "text": {"preview_url": False, "body": message_body}
                }
                with httpx.Client(timeout=10) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code in (200, 201):
                        print(f"[WHATSAPP DISPATCHED] Meta Cloud API sent OTP to {normalized_phone}")
                        return True
                    else:
                        print(f"[WHATSAPP WARNING] Meta API error {resp.status_code}: {resp.text}")
            except Exception as e:
                print(f"[WHATSAPP WARNING] Meta Cloud API exception: {e}")

        # 2. Attempt Twilio WhatsApp
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        twilio_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        if twilio_sid and twilio_token:
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
                auth = (twilio_sid, twilio_token)
                data = {
                    "From": twilio_from,
                    "To": f"whatsapp:{normalized_phone}",
                    "Body": message_body,
                }
                with httpx.Client(timeout=10) as client:
                    resp = client.post(url, auth=auth, data=data)
                    if resp.status_code in (200, 201):
                        print(f"[WHATSAPP DISPATCHED] Twilio sent OTP to {normalized_phone}")
                        return True
                    else:
                        print(f"[WHATSAPP WARNING] Twilio error {resp.status_code}: {resp.text}")
            except Exception as e:
                print(f"[WHATSAPP WARNING] Twilio exception: {e}")

        # 3. Simulated Development Fallback Log
        print("=" * 60)
        print("  [WHATSAPP DISPATCHED — SIMULATED LIVE HOOK]")
        print(f"  FROM: {sender_phone} ('School Portal Support')")
        print(f"  TO: {normalized_phone}")
        print(f"  RECIPIENT: {principal_name} — {school_name}")
        print(f"  6-DIGIT OTP: {code}")
        print(f"  EXPIRY: {expiry_minutes} minutes")
        print("=" * 60)
        return True
