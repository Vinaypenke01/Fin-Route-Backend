import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("masters", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomerReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("author_name", models.CharField(db_index=True, max_length=120)),
                ("business_name", models.CharField(blank=True, max_length=150)),
                ("role_title", models.CharField(default="Lender", max_length=100)),
                ("rating", models.PositiveIntegerField(default=5)),
                ("review_text", models.TextField()),
                ("avatar_url", models.CharField(blank=True, max_length=500)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], db_index=True, default="pending", max_length=20)),
                ("is_approved", models.BooleanField(db_index=True, default=False)),
            ],
            options={
                "verbose_name": "Customer Review",
                "verbose_name_plural": "Customer Reviews",
                "ordering": ["-created_at"],
            },
        ),
    ]
