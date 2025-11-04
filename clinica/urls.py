from django.urls import path
from . import views

urlpatterns = [
    # Página principal
    path('', views.index, name='index'),

    # Pacientes
    path('pacientes/', views.pacientes, name='pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('pacientes/nuevo/ajax/', views.crear_paciente_ajax, name='crear_paciente_ajax'),
    path('pacientes/<int:paciente_id>/editar/', views.editar_paciente, name='editar_paciente'),
    path('pacientes/<int:paciente_id>/eliminar/', views.eliminar_paciente, name='eliminar_paciente'),

    # Médicos
    path('medicos/', views.medicos, name='medicos'),
    path('medicos/nuevo/', views.crear_medico, name='crear_medico'),
    path('medicos/<int:medico_id>/eliminar/', views.eliminar_medico, name='eliminar_medico'),
    path('medicos/editar/<int:medico_id>/', views.editar_medico, name='editar_medico'),

    # Citas
    path('citas/', views.citas_lista, name='citas'),
    path('citas/nueva/', views.registrar_cita, name='registrar_cita'),
    path('citas/<int:cita_id>/', views.ver_cita, name='ver_cita'),
    path('citas/<int:cita_id>/editar/', views.editar_cita, name='editar_cita'),
    path('citas/<int:cita_id>/eliminar/', views.eliminar_cita, name='eliminar_cita'),

    # Contacto
    path('contacto/', views.contacto, name='contacto'),

    # Estadísticas bloqueadas/desbloqueadas
    path('citas/unlock/', views.unlock_stats, name='unlock_stats'),
    path('citas/lock/', views.lock_stats, name='lock_stats'),

    # 🔐 Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('register/', views.register_view, name='register'),


    # Compatibilidad para el template de registro (si lo usa)
    path('registro/', views.login_view, name='registro'),
]
