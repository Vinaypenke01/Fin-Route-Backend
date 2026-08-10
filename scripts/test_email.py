import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.conf import settings
import resend

def run_test():
    recipient = sys.argv[1] if len(sys.argv) > 1 else "digitalcoreservices6@gmail.com"
    print(f"\n🚀 Testing Resend Email Delivery Engine...")
    print(f"🔑 API Key Loaded: {settings.RESEND_API_KEY[:8]}...{settings.RESEND_API_KEY[-6:] if settings.RESEND_API_KEY else ''}")
    print(f"📧 Sender:          {settings.DEFAULT_FROM_EMAIL}")
    print(f"📩 Target Email:    {recipient}\n")

    resend.api_key = settings.RESEND_API_KEY
    try:
        res = resend.Emails.send({
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [recipient],
            "subject": "FinRoute — Email Delivery Test Verification",
            "html": "<p><strong>FinRoute Resend API is Live & Working!</strong></p>"
        })
        print(f"✅ SUCCESS! Email sent via Resend API.")
        print(f"🆔 Message ID: {res.get('id')}\n")
    except Exception as e:
        print(f"❌ ERROR: Failed to send email: {e}\n")

if __name__ == "__main__":
    run_test()
