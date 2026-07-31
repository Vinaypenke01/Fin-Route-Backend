"""
apps/accounts/management/commands/create_admin.py

Management command to create a Super Admin user.
Usage:
  python manage.py create_admin --mobile "+919999999999" --password "Admin@123456" --name "Super Admin"
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import User, AccountType


class Command(BaseCommand):
    help = "Creates a Super Admin user account for Finance ERP"

    def add_arguments(self, parser):
        parser.add_argument("--mobile", type=str, default="+919999999999", help="Mobile number (+91XXXXXXXXXX)")
        parser.add_argument("--password", type=str, default="Admin@123456", help="Super admin password")
        parser.add_argument("--name", type=str, default="Super Admin", help="Full name")
        parser.add_argument("--email", type=str, default="admin@digitalcore.co.in", help="Email address")

    def handle(self, *args, **options):
        mobile = options["mobile"]
        password = options["password"]
        name = options["name"]
        email = options["email"]

        if User.objects.filter(mobile_number=mobile).exists():
            user = User.objects.get(mobile_number=mobile)
            user.set_password(password)
            user.full_name = name
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.is_mobile_verified = True
            user.account_type = AccountType.ADMIN
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated existing user '{mobile}' to Super Admin."))
        else:
            User.objects.create_superuser(
                mobile_number=mobile,
                password=password,
                full_name=name,
                email=email,
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully created Super Admin user '{mobile}'."))

        self.stdout.write(self.style.SUCCESS(
            f"\nCredentials:\n  Mobile: {mobile}\n  Password: {password}\n  Role: Super Admin (admin)"
        ))
