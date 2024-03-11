# rectifier_app/models.py
from django.db import models

class RectifierCircuit(models.Model):
    alpha = models.FloatField()
    source_voltage = models.FloatField()

    class Meta:
        app_label = 'rectifier_app'  # Specify the app_label
