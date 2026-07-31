from django.apps import AppConfig


class GuestWorkspaceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.guest_workspace"
    verbose_name = "Guest Workspace"

    def ready(self):
        import sys
        if "runserver" in sys.argv or "manage.py" in sys.argv:
            try:
                from django.core.management import call_command
                call_command("makemigrations", "guest_workspace", interactive=False)
                call_command("makemigrations", "administration", interactive=False)
                call_command("migrate", interactive=False)
                self.backfill_existing_borrower_collections()
            except Exception as e:
                print("Auto-migration / backfill error:", e)

    def backfill_existing_borrower_collections(self):
        try:
            from datetime import date
            from apps.guest_workspace.models import CustomerProfile, CollectionEntry
            from apps.guest_workspace.services.collection_service import generate_receipt_number
            from apps.masters.models import CollectionStatus, PaymentMode

            status_obj = CollectionStatus.objects.filter(code="paid").first()
            mode_obj = PaymentMode.objects.first()

            existing_borrowers = CustomerProfile.objects.filter(
                is_existing_borrower=True,
                amount_already_collected__gt=0,
            )

            for customer in existing_borrowers:
                if not CollectionEntry.objects.filter(customer=customer).exists():
                    from datetime import timedelta
                    coll_date = customer.start_date or (customer.created_at.date() - timedelta(days=1) if customer.created_at else date.today() - timedelta(days=1))
                    receipt = generate_receipt_number(customer.workspace_id, coll_date)
                    CollectionEntry.objects.create(
                        workspace=customer.workspace,
                        customer=customer,
                        collected_by=customer.created_by,
                        receipt_number=receipt,
                        collection_date=coll_date,
                        expected_amount=customer.amount_already_collected,
                        collected_amount=customer.amount_already_collected,
                        status_id=status_obj.id if status_obj else 1,
                        payment_mode_id=mode_obj.id if mode_obj else 1,
                        remarks=f"Initial opening balance record for existing borrower ({customer.installments_paid_count or 0} past installments paid)",
                    )
        except Exception as e:
            print("Backfill error:", e)

