from django import forms
from .models import Paciente, Cita, Medico

# Formulario para Paciente
from django import forms
from .models import Paciente, Cita, Medico

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'dui', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'dui': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01234567-8'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
        }


# Formulario para Cita
class CitaForm(forms.ModelForm):
    nuevo_paciente_nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del paciente'})
    )
    nuevo_paciente_apellido = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido del paciente'})
    )
    nuevo_paciente_dui = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DUI del paciente'})
    )
    nuevo_paciente_telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del paciente'})
    )
    nuevo_paciente_direccion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección del paciente'})
    )

    class Meta:
        model = Cita
        fields = ['medico', 'fecha', 'motivo']
        widgets = {
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Motivo de la cita'}),
        }

    class Meta:
        model = Cita
        fields = ['paciente', 'medico', 'fecha', 'motivo']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Motivo de la cita'}),
        }

    def save(self, commit=True):
        """
        Sobrescribimos save para crear un paciente nuevo si se llenan los campos de nuevo paciente.
        """
        nuevo_nombre = self.cleaned_data.get('nuevo_paciente_nombre')
        nuevo_apellido = self.cleaned_data.get('nuevo_paciente_apellido')
        nuevo_dui = self.cleaned_data.get('nuevo_paciente_dui')
        nuevo_telefono = self.cleaned_data.get('nuevo_paciente_telefono', '')

        if nuevo_nombre and nuevo_apellido and nuevo_dui:
            paciente, created = Paciente.objects.get_or_create(
                nombre=nuevo_nombre,
                apellido=nuevo_apellido,
                dui=nuevo_dui,
                defaults={'telefono': nuevo_telefono}
            )
            self.instance.paciente = paciente

        return super().save(commit=commit)

# forms.py
from django import forms
from .models import Cita

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['medico', 'fecha', 'motivo']  # Excluir paciente

from django import forms
from .models import Paciente, Cita

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'dui', 'telefono', 'direccion']

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['medico', 'fecha', 'motivo']


# clinica/views.py
from django.shortcuts import render

def pacientes(request):
    return render(request, 'pacientes.html')

from django import forms
from .models import Cita, Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'dui', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del paciente'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido del paciente'}),
            'dui': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678-9'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 7777-8888'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección del paciente'}),
        }

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['medico', 'fecha', 'motivo']
        widgets = {
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Motivo de la cita'}),
        }
