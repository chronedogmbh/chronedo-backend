# Generated by Django 4.2.1 on 2023-05-10 16:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("watches", "0003_alter_brand_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="watch",
            name="location",
            field=models.CharField(default="USA", max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="watch",
            name="link",
            field=models.URLField(max_length=2000),
        ),
    ]
