from django import forms
from .models import Boleto

# Genera todas las horas de 00:00 a 23:00
HORA_CHOICES = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(24)]

class BoletoForm(forms.ModelForm):
    class Meta:
        model = Boleto
        fields = '__all__'
        widgets = {
            'fecha_viaje': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'hora_salida': forms.Select(
                choices=HORA_CHOICES,
                attrs={'class': 'form-select'}
            ),
        }
