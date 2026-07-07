from django.db import models


class Widget(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.name


class VisibleGadgetManager(models.Manager):
    """Default manager that hides archived rows (stand-in for soft-delete)."""

    def get_queryset(self):
        return super().get_queryset().filter(archived=False)


class Gadget(models.Model):
    """
    Model with a *filtering* default manager, used to prove object resolution
    goes through ``_default_manager`` (which hides archived rows) rather than
    ``_base_manager`` (which would expose them).
    """

    name = models.CharField(max_length=100)
    archived = models.BooleanField(default=False)

    objects = VisibleGadgetManager()  # _default_manager -- filters archived
    all_objects = models.Manager()  # noqa: DJ012  # base manager -- sees everything

    class Meta:
        base_manager_name = "all_objects"

    def __str__(self):
        return self.name
