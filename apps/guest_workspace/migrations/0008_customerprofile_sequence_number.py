from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("guest_workspace", "0007_customerprofile_installment_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerprofile",
            name="sequence_number",
            field=models.IntegerField(
                blank=True,
                db_index=True,
                help_text="Custom sequence or order number for borrower.",
                null=True,
            ),
        ),
    ]
