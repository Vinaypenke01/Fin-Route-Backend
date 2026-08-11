"""
Django Management Command: check_db
Usage: python manage.py check_db
Tests current database connection and prints database engine & status.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = "Check database connection status"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("🔍 Checking Database Connection..."))

        db_config = settings.DATABASES["default"]
        engine = db_config.get("ENGINE", "")
        host = db_config.get("HOST", "localhost")
        name = db_config.get("NAME", "")
        user = db_config.get("USER", "")

        self.stdout.write(f"⚙️ Engine: {engine.split('.')[-1]}")
        self.stdout.write(f"🌐 Host:   {host or 'localhost'}")
        self.stdout.write(f"📁 DB Name: {name}")
        self.stdout.write(f"👤 DB User: {user}\n")

        try:
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row and row[0] == 1:
                    self.stdout.write(self.style.SUCCESS("=================================================="))
                    self.stdout.write(self.style.SUCCESS("✅ SUCCESS: Database Connection is Working Perfectly!"))
                    self.stdout.write(self.style.SUCCESS("==================================================\n"))
                else:
                    self.stdout.write(self.style.ERROR("❌ ERROR: Query failed to return expected result."))
        except Exception as exc:
            self.stdout.write(self.style.ERROR("=================================================="))
            self.stdout.write(self.style.ERROR(f"❌ DATABASE CONNECTION FAILED: {exc}"))
            self.stdout.write(self.style.ERROR("=================================================="))
            if "postgres.railway.internal" in str(exc):
                self.stdout.write(self.style.WARNING("\n💡 EXPLANATION:"))
                self.stdout.write(self.style.WARNING("   'postgres.railway.internal' is Railway's Private Internal Network URL."))
                self.stdout.write(self.style.WARNING("   It ONLY works when deployed inside Railway's cloud containers."))
                self.stdout.write(self.style.WARNING("   To test locally from your laptop, use Railway's 'Public Networking URL'"))
                self.stdout.write(self.style.WARNING("   (e.g., postgresql://postgres:...@junction.proxy.rlwy.net:PORT/railway)"))
                self.stdout.write(self.style.WARNING("   OR set USE_SQLITE=True in .env for offline local development.\n"))
