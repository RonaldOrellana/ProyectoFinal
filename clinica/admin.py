from django.contrib import admin
from .models import Paciente, Medico, Cita, Servicio
from .models import ContactMessage

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'telefono', 'edad', 'medico')
    search_fields = ('nombre', 'apellido', 'telefono')

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'especialidad')
    search_fields = ('nombre', 'apellido', 'especialidad')

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'fecha')
    list_filter = ('fecha',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'asunto', 'creado_en')
    search_fields = ('nombre', 'email', 'mensaje', 'asunto')
    readonly_fields = ('creado_en',)
