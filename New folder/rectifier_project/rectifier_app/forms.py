# rectifier_app/forms.py
from django import forms
from .models import RectifierCircuit

class RectifierCircuitForm(forms.ModelForm):
    class Meta:
        model = RectifierCircuit
        fields = ['alpha', 'source_voltage']