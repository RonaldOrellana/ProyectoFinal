from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Paciente, Medico, Cita, Servicio
from .forms import PacienteForm, CitaForm, MedicoForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime

# -----------------------------
# VISTAS PRINCIPALES
# -----------------------------
def index(request):
    from django.db.models import Sum
    from django.utils import timezone
    citas = Cita.objects.all()
    total_citas = citas.count()
    total_citas_proximas = citas.filter(fecha__gt=timezone.now()).count()
    total_citas_hoy = citas.filter(fecha__date=timezone.now().date()).count()
    total_citas_realizadas = citas.filter(fecha__lt=timezone.now()).count()
    total_costos = citas.aggregate(total=Sum('servicio__precio'))['total'] or 0
    return render(request, 'index.html', {
        'total_citas': total_citas,
        'total_citas_proximas': total_citas_proximas,
        'total_citas_hoy': total_citas_hoy,
        'total_citas_realizadas': total_citas_realizadas,
        'total_costos': total_costos
    })

def pacientes(request):
    # Añadimos anotaciones para mostrar el último médico que atendió a cada paciente
    from django.db.models import OuterRef, Subquery

    # Subquery para obtener la última cita por fecha para cada paciente
    last_cita_qs = Cita.objects.filter(paciente=OuterRef('pk')).order_by('-fecha')

    pacientes = Paciente.objects.all().annotate(
        last_medico_nombre=Subquery(last_cita_qs.values('medico__nombre')[:1]),
        last_medico_apellido=Subquery(last_cita_qs.values('medico__apellido')[:1])
    )

    return render(request, 'pacientes.html', {'pacientes': pacientes})

def medicos(request):
    from django.db.models import Sum, Count
    from django.utils import timezone
    medicos = Medico.objects.all().order_by('apellido')
    citas = Cita.objects.all()
    total_citas = citas.count()
    total_citas_proximas = citas.filter(fecha__gt=timezone.now()).count()
    total_citas_hoy = citas.filter(fecha__date=timezone.now().date()).count()
    total_citas_realizadas = citas.filter(fecha__lt=timezone.now()).count()
    total_costos = citas.aggregate(total=Sum('servicio__precio'))['total'] or 0
    return render(request, 'medicos.html', {
        'medicos': medicos,
        'total_citas': total_citas,
        'total_citas_proximas': total_citas_proximas,
        'total_citas_hoy': total_citas_hoy,
        'total_citas_realizadas': total_citas_realizadas,
        'total_costos': total_costos
    })

def crear_medico(request):
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Médico registrado correctamente.')
            return redirect('medicos')
        else:
            messages.error(request, '⚠️ Por favor corrige los errores en el formulario.')
    else:
        form = MedicoForm()
    return render(request, 'clinica/crear_medico.html', {'form': form})

def eliminar_medico(request, medico_id):
    try:
        medico = get_object_or_404(Medico, id=medico_id)
        nombre_medico = f"Dr. {medico.nombre} {medico.apellido}"
        medico.delete()
        messages.success(request, f'✅ El médico {nombre_medico} ha sido eliminado correctamente.')
    except Exception as e:
        messages.error(request, '❌ No se pudo eliminar el médico. Puede tener citas asociadas.')
    return redirect('medicos')

def citas_lista(request):
    from django.db.models import Sum
    from django.utils import timezone
    citas = Cita.objects.all().order_by('-fecha')
    total_citas = citas.count()
    total_citas_proximas = citas.filter(fecha__gt=timezone.now()).count()
    total_citas_hoy = citas.filter(fecha__date=timezone.now().date()).count()
    total_citas_realizadas = citas.filter(fecha__lt=timezone.now()).count()
    total_costos = citas.aggregate(total=Sum('servicio__precio'))['total'] or 0
    # comprobar si el usuario desbloqueó las estadísticas con PIN
    stats_unlocked = request.session.get('stats_unlocked', False)
    return render(request, 'clinica/citas_lista.html', {
        'citas': citas,
        'total_citas': total_citas,
        'total_citas_proximas': total_citas_proximas,
        'total_citas_hoy': total_citas_hoy,
        'total_citas_realizadas': total_citas_realizadas,
        'total_costos': total_costos,
        'stats_unlocked': stats_unlocked
    })


def unlock_stats(request):
    """Comprueba el PIN (123) y guarda la bandera en la sesión para mostrar estadísticas."""
    if request.method == 'POST':
        pin = request.POST.get('pin', '').strip()
        if pin == '123':
            request.session['stats_unlocked'] = True
            messages.success(request, '✅ Estadísticas desbloqueadas.')
        else:
            messages.error(request, '❌ PIN incorrecto.')
    return redirect('citas')


def lock_stats(request):
    """Quita la bandera de sesión que permite ver estadísticas."""
    request.session.pop('stats_unlocked', None)
    messages.info(request, '🔒 Estadísticas ocultadas.')
    return redirect('citas')

from .forms import PacienteForm, CitaForm, MedicoForm
from .forms import ContactForm


def contacto(request):
    """Formulario de contacto: guarda el mensaje en la base de datos."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contacto = form.save()
            messages.success(request, '✅ Mensaje enviado. Gracias por contactarnos.')
            return redirect('contacto')
        else:
            messages.error(request, '⚠️ Por favor corrige los errores del formulario.')
    else:
        form = ContactForm()
    return render(request, 'contacto.html', {'form': form})

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

    # Preseleccionar servicio/medico si viene en query string ?servicio=Nombre
    selected_servicio_name = request.GET.get('servicio') if request.method == 'GET' else None
    selected_servicio_obj = None
    initial_cita = {}
    if selected_servicio_name:
        try:
            selected_servicio_obj = Servicio.objects.filter(nombre__iexact=selected_servicio_name).first() or Servicio.objects.filter(nombre__icontains=selected_servicio_name).first()
            if selected_servicio_obj and getattr(selected_servicio_obj, 'medico', None):
                initial_cita['medico'] = selected_servicio_obj.medico.id
        except Exception:
            selected_servicio_obj = None

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
            return redirect('citas')
        else:
            messages.error(request, "⚠️ Verifica los datos ingresados.")
    else:
        cita_form = CitaForm(initial=initial_cita)
        paciente_form = PacienteForm()

    return render(request, 'clinica/registrar_cita.html', {
        'cita_form': cita_form,
        'paciente_form': paciente_form,
        'pacientes': pacientes,
        'medicos': medicos,
        'selected_servicio': selected_servicio_obj.nombre if selected_servicio_obj else selected_servicio_name
    })



def editar_paciente(request, paciente_id):
    try:
        paciente = get_object_or_404(Paciente, id=paciente_id)
        if request.method == 'POST':
            form = PacienteForm(request.POST, instance=paciente)
            if form.is_valid():
                form.save()
                messages.success(request, '✅ Paciente actualizado correctamente.')
                return redirect('pacientes')
            else:
                messages.error(request, '⚠️ Por favor verifica los datos ingresados.')
        else:
            form = PacienteForm(instance=paciente)
        
        return render(request, 'clinica/editar_paciente.html', {
            'form': form,
            'paciente': paciente
        })
    except Exception as e:
        messages.error(request, f'❌ Error al editar el paciente: {str(e)}')
        return redirect('pacientes')

def eliminar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    paciente.delete()
    messages.success(request, "✅ Paciente eliminado correctamente.")
    return redirect('pacientes')


def iniciar_sesion(request):
    """Vista para iniciar sesión de usuarios con username y password."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, '✅ Has iniciado sesión correctamente.')
            # redirigir a next si existe
            next_url = request.GET.get('next') or request.POST.get('next') or 'index'
            return redirect(next_url)
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos.')
            return render(request, 'clinica/iniciar_sesion.html', {'username': username})
    else:
        return render(request, 'clinica/iniciar_sesion.html')


def cerrar_sesion(request):
    """Cerrar sesión y redirigir a la página principal."""
    auth_logout(request)
    messages.success(request, '✅ Has cerrado sesión correctamente.')
    return redirect('index')


def registro(request):
    """Registro rápido de usuarios usando UserCreationForm.
    Después del registro se autentica al usuario y se redirige al índice.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # opción: agregar email si fue provisto
            email = request.POST.get('email')
            if email:
                user.email = email
                user.save()
            # iniciar sesión automáticamente
            auth_user = authenticate(request, username=user.username, password=request.POST.get('password1'))
            if auth_user is not None:
                auth_login(request, auth_user)
            messages.success(request, '✅ Registro completado. Bienvenido.')
            return redirect('index')
        else:
            messages.error(request, '⚠️ Por favor corrige los errores del formulario de registro.')
    else:
        form = UserCreationForm()
    return render(request, 'clinica/registro.html', {'form': form})

