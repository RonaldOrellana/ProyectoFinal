from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Paciente, Medico, Cita, Servicio
from .forms import PacienteForm, CitaForm
from datetime import datetime

# -----------------------------
# VISTAS PRINCIPALES
# -----------------------------
def index(request):
    servicios = Servicio.objects.all()[:8]
    return render(request, 'index.html', {'servicios': servicios})

def pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'pacientes.html', {'pacientes': pacientes})

def medicos(request):
    medicos = Medico.objects.all()
    return render(request, 'medicos.html', {'medicos': medicos})

def citas_lista(request):
    citas = Cita.objects.all().order_by('-fecha')
    return render(request, 'clinica/citas_lista.html', {'citas': citas})

def contacto(request):
    return render(request, 'contacto.html')

# -----------------------------
# PACIENTES
# -----------------------------
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Paciente registrado correctamente.')
            return redirect('pacientes')
        else:
            messages.error(request, '⚠️ Por favor corrige los errores en el formulario.')
    else:
        form = PacienteForm()
    return render(request, 'clinica/crear_paciente.html', {'form': form})

def crear_paciente_ajax(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        dui = request.POST.get('dui', '').strip()

        if not nombre or not apellido or not dui:
            return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios.'})

        if Paciente.objects.filter(dui=dui).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un paciente con este DUI.'})

        paciente = Paciente.objects.create(nombre=nombre, apellido=apellido, dui=dui)
        return JsonResponse({
            'success': True,
            'id': paciente.id,
            'nombre_completo': f"{paciente.nombre} {paciente.apellido}"
        })
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

# -----------------------------
# CITAS
# -----------------------------
def registrar_cita(request):
    if request.method == 'POST':
        paciente_form = PacienteForm(request.POST)
        cita_form = CitaForm(request.POST)
        if paciente_form.is_valid() and cita_form.is_valid():
            paciente = paciente_form.save()
            cita = cita_form.save(commit=False)
            cita.paciente = paciente
            cita.save()
            messages.success(request, "✅ Cita registrada correctamente.")
            return redirect('citas')
        else:
            messages.error(request, "⚠️ Verifica los datos ingresados.")
    else:
        paciente_form = PacienteForm()
        cita_form = CitaForm()

    return render(request, 'clinica/registrar_cita.html', {
        'form': cita_form,
        'paciente_form': paciente_form
    })

def ver_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    return render(request, 'clinica/ver_cita.html', {'cita': cita})

def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Cita actualizada.')
            return redirect('citas')
        else:
            messages.error(request, '⚠️ Verifica los datos ingresados.')
    else:
        form = CitaForm(instance=cita)
    return render(request, 'clinica/editar_cita.html', {'form': form})

def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, '❌ Cita eliminada.')
        return redirect('citas')
    return render(request, 'clinica/eliminar_cita.html', {'cita': cita})

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
    path('citas/nueva/', views.registrar_cita, name='registrar_cita'),  # Registrar cita
    path('citas/<int:cita_id>/', views.ver_cita, name='ver_cita'),
    path('citas/<int:cita_id>/editar/', views.editar_cita, name='editar_cita'),
    path('citas/<int:cita_id>/eliminar/', views.eliminar_cita, name='eliminar_cita'),

    # Contacto
    path('contacto/', views.contacto, name='contacto'),
]
