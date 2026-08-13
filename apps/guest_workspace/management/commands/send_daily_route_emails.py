"""
send_daily_route_emails.py — Django Management Command for Automated Evening Route Collection Email Cron-Job.

Run timing: 11:00 PM to 11:59 PM (end of day).
Execution: python manage.py send_daily_route_emails
Cron expression: 0 23 * * *
"""

import logging
from datetime import date as dt_date
from django.core.management.base import BaseCommand
from apps.guest_workspace.models import GuestWorkspace, CollectionLine
from apps.guest_workspace.services.route_email_report_service import RouteEmailReportService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Automated evening cron-job to generate and send daily collection Excel/CSV reports to guest users for their scheduled route lines."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Target date YYYY-MM-DD to process (defaults to today)",
        )
        parser.add_argument(
            "--workspace-id",
            type=str,
            help="Filter specific workspace public ID for testing",
        )

    def handle(self, *args, **options):
        date_str = options.get("date")
        target_date = dt_date.today()
        if date_str:
            try:
                from datetime import datetime
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Invalid date format: {date_str}. Use YYYY-MM-DD"))
                return

        today_weekday = target_date.strftime("%A").lower()
        self.stdout.write(self.style.SUCCESS(f"🚀 Starting Evening Route Email Cron-Job for {today_weekday.capitalize()} ({target_date})..."))

        workspaces_qs = GuestWorkspace.objects.filter(status="active")
        workspace_id = options.get("workspace_id")
        if workspace_id:
            workspaces_qs = workspaces_qs.filter(public_id=workspace_id)

        processed_count = 0
        emails_sent_count = 0

        for ws in workspaces_qs:
            lines = CollectionLine.objects.filter(workspace=ws, is_active=True).prefetch_related("day_schedules")

            matching_lines = []
            for line in lines:
                # Check if line operates on today's weekday
                if any(sched.day_of_week.lower() == today_weekday for sched.all_schedules() if hasattr(sched, "day_of_week")):
                    matching_lines.append(line)
                elif hasattr(line, "day_schedules"):
                    # Check LineDaySchedule objects
                    if line.day_schedules.filter(day_of_week__iexact=today_weekday).exists():
                        matching_lines.append(line)

            if not matching_lines:
                # If no specific line match but workspace has active customers, process overall line
                if CollectionLine.objects.filter(workspace=ws).count() == 0:
                    matching_lines = [None]

            for line in matching_lines:
                processed_count += 1
                line_name = line.name if line else "All Lines"
                self.stdout.write(f"  ➜ Processing Workspace '{ws.name}' | Line '{line_name}' | Date {target_date}...")

                sent = RouteEmailReportService.send_route_email(
                    workspace=ws,
                    line=line,
                    target_date=target_date,
                )

                if sent:
                    emails_sent_count += 1
                    self.stdout.write(self.style.SUCCESS(f"    ✅ Email report sent successfully for '{line_name}'"))
                else:
                    self.stdout.write(self.style.WARNING(f"    ⚠️ Failed or skipped email report for '{line_name}'"))

        self.stdout.write(self.style.SUCCESS(
            f"🎉 Completed Evening Route Email Cron-Job! Processed: {processed_count} lines | Emails Sent: {emails_sent_count}."
        ))
