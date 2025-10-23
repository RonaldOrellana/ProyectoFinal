from django.shortcuts import render
from .models import Paciente, Medico, Cita, Servicio

def index(request):
    servicios = Servicio.objects.all()[:8]
    return render(request, 'index.html', {'servicios': servicios})

def pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'pacientes.html', {'pacientes': pacientes})

def medicos(request):
    medicos = Medico.objects.all()
    return render(request, 'medicos.html', {'medicos': medicos})

def citas(request):
    citas = Cita.objects.order_by('-fecha')[:50]
    return render(request, 'citas.html', {'citas': citas})

def contacto(request):
    return render(request, 'contacto.html')
