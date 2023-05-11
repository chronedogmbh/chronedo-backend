from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedAbstractModel(models.Model):  # AccountabilityMixin
    """
    An abstract model that adds a ``created_at`` and ``modified_at`` field to a model that inherits this class.
    The fields are automatically set whenever an object's ``save`` function is called. See:
    https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.DateField.auto_now and
    https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.DateField.auto_now_add for more
    information.
    """

    created_at = models.DateTimeField(
        _("created at"), auto_now_add=True, editable=False
    )
    modified_at = models.DateTimeField(_("modified_at"), auto_now=True, editable=False)

    class Meta:
        abstract = True
