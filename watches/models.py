from django.conf import settings
from django.db import models

from core.abstract import TimestampedAbstractModel


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
