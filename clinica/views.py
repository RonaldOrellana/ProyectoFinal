from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.db.models import Sum, OuterRef, Subquery
from django.utils import timezone

from .models import Paciente, Medico, Cita, Servicio
from .forms import PacienteForm, MedicoForm, CitaForm, ContactForm

# =====================================================
# ✅ INICIO (RESTRINGIDO — SOLO USUARIOS LOGUEADOS)
# =====================================================
@login_required(login_url='login')
def index(request):
    servicios = Servicio.objects.all()
    return render(request, 'clinica/index.html', {'servicios': servicios})

# =====================================================
# ✅ LOGIN / REGISTER / LOGOUT
# =====================================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')  # Si ya está logueado, mándalo a inicio

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {username} 👋')
            return redirect('index')  # Redirige a tu página principal
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return redirect('login')

    return render(request, 'clinica/login.html')

def cerrar_sesion(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        print("📩 Datos recibidos:", username, email)  # Debug

        if not username or not password1:
            messages.error(request, "Debe llenar todos los campos.")
            return redirect('login')

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('login')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ese usuario ya existe.")
            return redirect('login')

        # ✅ Crear usuario correctamente
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        user.save()
        print("✅ Usuario guardado correctamente")

        messages.success(request, "Cuenta creada. Ahora inicia sesión 💫")
        return redirect('login')

    return redirect('login')
# =====================================================
# ✅ PACIENTES
# =====================================================
@login_required(login_url='login')
def pacientes(request):
    last_cita_qs = Cita.objects.filter(paciente=OuterRef('pk')).order_by('-fecha')
    pacientes = Paciente.objects.all().annotate(
        last_medico_nombre=Subquery(last_cita_qs.values('medico__nombre')[:1]),
        last_medico_apellido=Subquery(last_cita_qs.values('medico__apellido')[:1])
    )
    return render(request, 'pacientes.html', {'pacientes': pacientes})

@login_required(login_url='login')
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente creado ✅')
            return redirect('pacientes')
        messages.error(request, 'Corrige los errores')
    else:
        form = PacienteForm()
    return render(request, 'clinica/crear_paciente.html', {'form': form})

@login_required(login_url='login')
def crear_paciente_ajax(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        dui = request.POST.get('dui')
        if Paciente.objects.filter(dui=dui).exists():
            return JsonResponse({'success': False, 'error': 'Este paciente ya existe'})
        paciente = Paciente.objects.create(nombre=nombre, apellido=apellido, dui=dui)
        return JsonResponse({
            'success': True,
            'id': paciente.id,
            'nombre_completo': f"{paciente.nombre} {paciente.apellido}"
        })
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required(login_url='login')
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente actualizado ✅")
            return redirect('pacientes')
        messages.error(request, "Corrige los errores")
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'clinica/editar_paciente.html', {'form': form, 'paciente': paciente})

@login_required(login_url='login')
def eliminar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    paciente.delete()
    messages.success(request, "Paciente eliminado ✅")
    return redirect('pacientes')

# =====================================================
# ✅ MÉDICOS
# =====================================================
@login_required(login_url='login')
def medicos(request):
    medicos = Medico.objects.all().order_by('apellido')
    citas = Cita.objects.all()
    return render(request, 'medicos.html', {
        'medicos': medicos,
        'total_citas': citas.count(),
        'total_citas_proximas': citas.filter(fecha__gt=timezone.now()).count(),
        'total_citas_hoy': citas.filter(fecha__date=timezone.now().date()).count(),
        'total_citas_realizadas': citas.filter(fecha__lt=timezone.now()).count(),
        'total_costos': citas.aggregate(total=Sum('servicio__precio'))['total'] or 0
    })

@login_required(login_url='login')
def crear_medico(request):
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Médico creado ✅")
            return redirect('medicos')
        messages.error(request, "Corrige los errores")
    else:
        form = MedicoForm()
    return render(request, 'clinica/crear_medico.html', {'form': form})

@login_required(login_url='login')
def editar_medico(request, medico_id):
    medico = get_object_or_404(Medico, id=medico_id)
    if request.method == 'POST':
        form = MedicoForm(request.POST, instance=medico)
        if form.is_valid():
            form.save()
            return redirect('medicos')
    else:
        form = MedicoForm(instance=medico)
    return render(request, 'clinica/editar_medico.html', {'form': form, 'medico': medico})

@login_required(login_url='login')
def eliminar_medico(request, medico_id):
    medico = get_object_or_404(Medico, id=medico_id)
    medico.delete()
    messages.success(request, "Médico eliminado ✅")
    return redirect('medicos')

# =====================================================
# ✅ CITAS
# =====================================================
@login_required(login_url='login')
def citas_lista(request):
    citas = Cita.objects.all().order_by('-fecha')
    stats_unlocked = request.session.get('stats_unlocked', False)
    return render(request, 'clinica/citas_lista.html', {
        'citas': citas,
        'total_citas': citas.count(),
        'total_citas_proximas': citas.filter(fecha__gt=timezone.now()).count(),
        'total_citas_hoy': citas.filter(fecha__date=timezone.now().date()).count(),
        'total_citas_realizadas': citas.filter(fecha__lt=timezone.now()).count(),
        'total_costos': citas.aggregate(total=Sum('servicio__precio'))['total'] or 0,
        'stats_unlocked': stats_unlocked
    })

@login_required(login_url='login')
def registrar_cita(request):
    servicios = Servicio.objects.all()
    pacientes = Paciente.objects.all()
    medicos = Medico.objects.all()

    if request.method == 'POST':
        paciente_form = PacienteForm(request.POST)
        cita_form = CitaForm(request.POST)
        if paciente_form.is_valid() and cita_form.is_valid():
            paciente = paciente_form.save()
            cita = cita_form.save(commit=False)
            cita.paciente = paciente
            cita.save()
            messages.success(request, "Cita registrada ✅")
            return redirect('citas')
        messages.error(request, "Corrige los errores")
    else:
        paciente_form = PacienteForm()
        cita_form = CitaForm()

    return render(request, 'clinica/registrar_cita.html', {
        'servicios': servicios,
        'pacientes': pacientes,
        'medicos': medicos,
        'paciente_form': paciente_form,
        'cita_form': cita_form
    })

@login_required(login_url='login')
def ver_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    return render(request, 'ver_cita.html', {'cita': cita})

@login_required(login_url='login')
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    pacientes = Paciente.objects.all()
    medicos = Medico.objects.all()

    if request.method == 'POST':
        paciente_id = request.POST.get('paciente')
        medico_id = request.POST.get('medico')
        fecha = request.POST.get('fecha')
        motivo = request.POST.get('motivo')
        cita.paciente_id = paciente_id
        cita.medico_id = medico_id
        cita.fecha = fecha
        cita.motivo = motivo
        cita.save()
        messages.success(request, '✅ Cita actualizada correctamente.')
        return redirect('citas')

    return render(request, 'clinica/editar_cita.html', {
        'cita': cita,
        'pacientes': pacientes,
        'medicos': medicos,
    })

@login_required(login_url='login')
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, '❌ Cita eliminada.')
        return redirect('citas')
    return render(request, 'clinica/eliminar_cita.html', {'cita': cita})

# =====================================================
# ✅ ESTADÍSTICAS (PIN)
# =====================================================
@login_required(login_url='login')
def unlock_stats(request):
    if request.method == 'POST':
        if request.POST.get('pin') == '123':
            request.session['stats_unlocked'] = True
            messages.success(request, "Estadísticas desbloqueadas ✅")
        else:
            messages.error(request, "PIN incorrecto ❌")
    return redirect('citas')

@login_required(login_url='login')
def lock_stats(request):
    request.session.pop('stats_unlocked', None)
    messages.info(request, "Estadísticas ocultadas")
    return redirect('citas')

# =====================================================
# ✅ CONTACTO
# =====================================================
def contacto(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mensaje enviado ✅")
            return redirect('contacto')
        messages.error(request, "Corrige los errores")
    else:
        form = ContactForm()
    return render(request, 'contacto.html', {'form': form})
