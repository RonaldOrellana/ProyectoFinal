from django.contrib import admin
from .models import Paciente, Medico, Cita, Servicio

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'correo', 'telefono')
    search_fields = ('nombre', 'apellido', 'correo')

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'especialidad', 'correo')
    search_fields = ('nombre', 'apellido', 'especialidad')

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'fecha')
    list_filter = ('fecha',)
