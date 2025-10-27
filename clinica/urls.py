from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Pacientes
    path('pacientes/', views.pacientes, name='pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('pacientes/nuevo/ajax/', views.crear_paciente_ajax, name='crear_paciente_ajax'),

    # Médicos
    path('medicos/', views.medicos, name='medicos'),

    # Citas
    path('citas/', views.citas_lista, name='citas'),  # Lista de citas
    path('citas/nueva/', views.registrar_cita, name='registrar_cita'),  # Registrar nueva cita
    path('citas/<int:cita_id>/', views.ver_cita, name='ver_cita'),
    path('citas/<int:cita_id>/editar/', views.editar_cita, name='editar_cita'),
    path('citas/<int:cita_id>/eliminar/', views.eliminar_cita, name='eliminar_cita'),

    # Contacto
    path('contacto/', views.contacto, name='contacto'),
]
