from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pacientes/', views.pacientes, name='pacientes'),
    path('medicos/', views.medicos, name='medicos'),
    path('citas/', views.citas, name='citas'),
    path('contacto/', views.contacto, name='contacto'),
]
