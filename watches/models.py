from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.abstract import TimestampedAbstractModel

from .tasks import scrape_watches


class Brand(TimestampedAbstractModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Watch(TimestampedAbstractModel):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.ForeignKey(Brand, related_name="watches", on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    link = models.URLField(max_length=2000)
    image = models.URLField(max_length=2000)

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="likes"
    )

    def __str__(self):
        return self.title


class Task(TimestampedAbstractModel):
    class CountryChoices(models.TextChoices):
        AT = "AT", "AT"
        BR = "BR", "BR"
        BG = "BG", "BG"
        CA = "CA", "CA"
        CZ = "CZ", "CZ"
        FR = "FR", "FR"
        DE = "DE", "DE"
        GR = "GR", "GR"
        IT = "IT", "IT"
        JP = "JP", "JP"
        NO = "NO", "NO"
        PL = "PL", "PL"
        SG = "SG", "SG"
        ES = "ES", "ES"
        SE = "SE", "SE"
        CH = "CH", "CH"
        NL = "NL", "NL"
        AE = "AE", "AE"
        UK = "UK", "UK"
        US = "US", "US"

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"

    class BrandChoices(models.TextChoices):
        ROLEX = "rolex", "Rolex"
        IWC = "iwc", "IWC"
        OMEGA = "omega", "Omega"
        BREITLING = "breitling", "Breitling"
        AUDEMARSPIGUET = "audemarspiguet", "Audemars Piguet"
        HUBLOT = "hublot", "Hublot"
        PANERAI = "panerai", "Panerai"
        PATEKPHILIPPE = "patekphilippe", "Patek Philippe"
        TUDOR = "tudor", "Tudor"

    class PerPageChoices(models.IntegerChoices):
        THIRTY = 30
        SIXTY = 60
        ONE_HUNDRED_TWENTY = 120

    title = models.CharField(max_length=255)
    country = models.CharField(max_length=2, choices=CountryChoices.choices)
    status = models.CharField(
        max_length=12, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    brand = models.CharField(max_length=20, choices=BrandChoices.choices)
    per_page = models.IntegerField(
        choices=PerPageChoices.choices, default=PerPageChoices.THIRTY
    )
    max_pages = models.IntegerField(default=1)

    def __str__(self):
        return self.title


@receiver(post_save, sender=Task)
def run_task(sender, instance, created, **kwargs):
    if created:
        scrape_watches.delay(instance.id)
