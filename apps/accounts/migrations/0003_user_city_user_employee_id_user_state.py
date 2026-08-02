# Generated manually for User profile fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_contactinquiry_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="city",
            field=models.CharField(blank=True, default="", max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="employee_id",
            field=models.CharField(blank=True, default="", max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="state",
            field=models.CharField(blank=True, default="", max_length=100, null=True),
        ),
    ]
