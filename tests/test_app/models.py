from django.db import models


class Widget(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.name
