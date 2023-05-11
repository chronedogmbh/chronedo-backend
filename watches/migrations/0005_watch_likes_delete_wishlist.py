# Generated by Django 4.2.1 on 2023-05-10 17:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("watches", "0004_watch_location_alter_watch_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="watch",
            name="likes",
            field=models.ManyToManyField(
                blank=True, related_name="likes", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.DeleteModel(
            name="Wishlist",
        ),
    ]
