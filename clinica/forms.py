from django import forms
from .models import Cita

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['paciente', 'medico', 'fecha', 'motivo']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type':'datetime-local'}),
        }
