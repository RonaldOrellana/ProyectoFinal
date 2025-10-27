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

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cita, Paciente, Medico
from .forms import CitaForm, PacienteForm

def registrar_cita(request):
    pacientes = Paciente.objects.all().order_by('nombre')
    medicos = Medico.objects.all().order_by('nombre')

    if request.method == 'POST':
        cita_form = CitaForm(request.POST)
        paciente_form = PacienteForm(request.POST)

        # Si el usuario escribió un nuevo paciente, lo guardamos primero
        if paciente_form.is_valid() and cita_form.is_valid():
            # Guardar nuevo paciente
            nuevo_paciente = paciente_form.save()
            
            # Asignar el paciente recién creado a la cita
            cita = cita_form.save(commit=False)
            cita.paciente = nuevo_paciente
            cita.save()

            messages.success(request, "✅ Cita y paciente registrados correctamente.")
            return redirect('citas_lista')
        else:
            messages.error(request, "⚠️ Verifica los datos ingresados.")
    else:
        cita_form = CitaForm()
        paciente_form = PacienteForm()

    return render(request, 'clinica/registrar_cita.html', {
        'cita_form': cita_form,
        'paciente_form': paciente_form,
        'pacientes': pacientes,
        'medicos': medicos
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Medico

def eliminar_medico(request, id):
    medico = get_object_or_404(Medico, id=id)

    if request.method == 'POST':
        medico.delete()
        messages.success(request, '✅ El médico fue eliminado correctamente.')
        return redirect('medicos')

    return render(request, 'clinica/eliminar_medico.html', {'medico': medico})
