# Generated by Django 4.1.3 on 2023-08-17 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("watches", "0006_task"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="country",
            field=models.CharField(
                choices=[
                    ("AT", "AT"),
                    ("BR", "BR"),
                    ("BG", "BG"),
                    ("CA", "CA"),
                    ("CZ", "CZ"),
                    ("FR", "FR"),
                    ("DE", "DE"),
                    ("GR", "GR"),
                    ("IT", "IT"),
                    ("JP", "JP"),
                    ("NO", "NO"),
                    ("PL", "PL"),
                    ("SG", "SG"),
                    ("ES", "ES"),
                    ("SE", "SE"),
                    ("CH", "CH"),
                    ("NL", "NL"),
                    ("AE", "AE"),
                    ("UK", "UK"),
                    ("US", "US"),
                ],
                max_length=2,
            ),
        ),
    ]