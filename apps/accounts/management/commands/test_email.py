"""
Django Management Command: test_email
Usage: python manage.py test_email --to=your_email@example.com
Tests Resend API email delivery service and reports result.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test Resend API Email service delivery"

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            type=str,
            default="digitalcoreservices6@gmail.com",
            help="Recipient email address for test email",
        )

    def handle(self, *args, **options):
        recipient = options["to"]
        self.stdout.write(self.style.NOTICE(f"🚀 Starting Resend Email Service Test to: {recipient}"))

        resend_key = getattr(settings, "RESEND_API_KEY", None)
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "FinRoute <info@fin-route.site>")

        self.stdout.write(f"🔑 RESEND_API_KEY Configured: {'YES (***' + resend_key[-6:] + ')' if resend_key else 'NO'}")
        self.stdout.write(f"📧 Sender Address:            {from_email}")
        self.stdout.write(f"📩 Target Recipient:          {recipient}\n")

        if not resend_key:
            self.stdout.write(self.style.ERROR("❌ ERROR: RESEND_API_KEY is not configured in settings or .env file."))
            return

        try:
            email_payload = {
                "from": from_email,
                "to": [recipient],
                "subject": "FinRoute — Email Verification & Service Test",
                "html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; color: #333; max-width: 600px; border: 1px solid #e0e0e0; border-radius: 8px;">
                    <h2 style="color: #2563eb; margin-top: 0;">FinRoute Email Service Working! ✅</h2>
                    <p>Hello,</p>
                    <p>This is an automated test email confirming that the <strong>FinRoute Resend Email Integration</strong> is active and delivering emails successfully.</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
                    <ul style="padding-left: 20px; font-size: 13px; color: #555;">
                        <li><strong>Sender Address:</strong> {from_email}</li>
                        <li><strong>Recipient Address:</strong> {recipient}</li>
                        <li><strong>Delivery Engine:</strong> Resend REST API</li>
                        <li><strong>Status:</strong> Active & Functional</li>
                    </ul>
                    <p style="font-size: 12px; color: #888; margin-bottom: 0;">Sent by FinRoute Micro-Lender Engine</p>
                </div>
                """,
            }

            resend_id = None
            self.stdout.write("⏳ Sending email via Resend REST API...")

            try:
                import resend
                resend.api_key = resend_key
                response = resend.Emails.send(email_payload)
                resend_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", str(response))
            except (ImportError, Exception):
                import urllib.request
                import json

                req_data = json.dumps(email_payload).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.resend.com/emails",
                    data=req_data,
                    headers={
                        "Authorization": f"Bearer {resend_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "FinRoute/1.0",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    resend_id = resp_data.get("id")

            self.stdout.write(self.style.SUCCESS(f"\n=================================================="))
            self.stdout.write(self.style.SUCCESS(f"✅ SUCCESS: Test Email Sent Successfully via Resend!"))
            self.stdout.write(self.style.SUCCESS(f"🆔 Resend Message ID: {resend_id}"))
            self.stdout.write(self.style.SUCCESS(f"📩 Delivered To:       {recipient}"))
            self.stdout.write(self.style.SUCCESS(f"==================================================\n"))

        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"\n=================================================="))
            self.stdout.write(self.style.ERROR(f"❌ FAILURE: Failed to send test email via Resend API."))
            self.stdout.write(self.style.ERROR(f"⚠️ Exception Error: {exc}"))
            self.stdout.write(self.style.ERROR(f"==================================================\n"))
