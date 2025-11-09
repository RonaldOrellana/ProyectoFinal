from django.db import models

from django.db import models

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dui = models.CharField(max_length=10, unique=True)
    telefono = models.CharField(max_length=9, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    edad = models.PositiveIntegerField(blank=True, null=True)
    medico = models.ForeignKey('Medico', on_delete=models.SET_NULL, blank=True, null=True, related_name='pacientes')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


# Modelo Medico
class Medico(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True)
    correo = models.EmailField(unique=True, blank=True)

    def __str__(self):
        return f"Dr. {self.nombre} {self.apellido} - {self.especialidad}"

# Modelo Servicio
class Servicio(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name="servicios", null=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nombre


# Modelo Cita
class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='citas')
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True, blank=True, related_name='citas')
    fecha = models.DateTimeField()
    motivo = models.TextField(blank=True)

    def __str__(self):
        return f"Cita: {self.paciente} con {self.medico} el {self.fecha}"


# Mensajes de contacto enviados desde la web
class ContactMessage(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    asunto = models.CharField(max_length=200, blank=True)
    mensaje = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} <{self.email}> - {self.asunto or 'Sin asunto'}"
from django import forms
from .models import Cita

from django import forms
from .models import Cita, Medico

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo una especialidad única (sin repetir)
        especialidades = Medico.objects.values_list('especialidad', flat=True).distinct()
        self.fields['medico'].queryset = Medico.objects.filter(especialidad__in=especialidades).distinct()
        # Mostrar el nombre de la especialidad en lugar del nombre del médico
        self.fields['medico'].label_from_instance = lambda obj: obj.especialidad

