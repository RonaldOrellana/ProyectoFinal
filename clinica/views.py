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
    paciente_form = PacienteForm()
    cita_form = CitaForm()
    
    # Todos los servicios disponibles
    servicios = Servicio.objects.all()
    
    # Las primeras 6 como destacadas (puedes cambiar)
    especialidades_destacadas = Servicio.objects.all()[:6]

    context = {
        'paciente_form': paciente_form,
        'cita_form': cita_form,
        'servicios': servicios,
        'especialidades_destacadas': especialidades_destacadas
    }
    return render(request, 'registrar_cita.html', context)

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

    context = {
        'cita': cita,
        'pacientes': pacientes,
        'medicos': medicos,
    }
    return render(request, 'clinica/editar_cita.html', context)


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

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Paciente, Medico, Servicio
from .forms import CitaForm, PacienteForm

def registrar_cita(request):
    pacientes = Paciente.objects.all().order_by('nombre')
    medicos = Medico.objects.all().order_by('nombre')
    servicios = Servicio.objects.all().order_by('nombre')  # <-- Traemos todos los servicios

    # Preseleccionar servicio si viene en query string ?servicio=Nombre
    selected_servicio_name = request.GET.get('servicio') if request.method == 'GET' else None
    selected_servicio_obj = None
    initial_cita = {}
    if selected_servicio_name:
        try:
            selected_servicio_obj = Servicio.objects.filter(nombre__iexact=selected_servicio_name).first() \
                                   or Servicio.objects.filter(nombre__icontains=selected_servicio_name).first()
            if selected_servicio_obj and getattr(selected_servicio_obj, 'medico', None):
                initial_cita['medico'] = selected_servicio_obj.medico.id
        except Exception:
            selected_servicio_obj = None

    if request.method == 'POST':
        cita_form = CitaForm(request.POST)
        paciente_form = PacienteForm(request.POST)

        # Guardar nuevo paciente si se ingresó
        if paciente_form.is_valid() and cita_form.is_valid():
            nuevo_paciente = paciente_form.save()
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
        'servicios': servicios,  # <-- Pasamos los servicios al template
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

from django.shortcuts import render, get_object_or_404
from .models import Cita

def ver_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    context = {
        'cita': cita
    }
    return render(request, 'ver_cita.html', context)

def editar_medico(request, id):
    medico = get_object_or_404(Medico, id=id)
    # tu lógica del formulario de edición aquí

def editar_medico(request, medico_id):
    medico = get_object_or_404(Medico, id=medico_id)
    
    if request.method == 'POST':
        form = MedicoForm(request.POST, request.FILES, instance=medico)
        if form.is_valid():
            form.save()
            return redirect('medicos')  # 👈 nombre de tu lista
    else:
        form = MedicoForm(instance=medico)
    
    return render(request, 'clinica/editar_medico.html', {'form': form, 'medico': medico})

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

# ✅ Página principal: solo usuarios logueados
def index(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Si no ha iniciado sesión → login
    return render(request, 'clinica/index.html')  # Si está logueado → muestra inicio


# ✅ Página de inicio de sesión y registro
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')  # Si ya está logueado → va al inicio

    login_error = None
    register_error = None

    # --- LOGIN ---
    if request.method == 'POST' and 'login' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            login_error = "Usuario o contraseña incorrectos"

    # --- REGISTRO ---
    if request.method == 'POST' and 'register' in request.POST:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cuenta creada con éxito 🎉")
            return redirect('index')
        else:
            register_error = "Por favor, corrige los errores."
    else:
        form = UserCreationForm()

    context = {
        'login_error': login_error,
        'register_error': register_error,
        'register_form': form,
    }
    return render(request, 'clinica/login.html', context)


# ✅ Cierre de sesión
def cerrar_sesion(request):
    logout(request)
    return redirect('login')  # Redirige directamente al login limpio

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def index(request):
    return render(request, 'clinica/index.html')



def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ese usuario ya existe')
            return redirect('register')

        # Crear usuario
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, 'Usuario creado correctamente. Ahora puedes iniciar sesión.')
        return redirect('login')

    return render(request, 'registrar.html')

from .models import Servicio


from django.contrib.auth.decorators import login_required
from .models import Servicio

@login_required(login_url='login')
def index(request):
    servicios = Servicio.objects.all()  # ✅ Traemos solo servicios

    return render(request, 'clinica/index.html', {
        'servicios': servicios
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Servicio
from .forms import PacienteForm, CitaForm
from django.contrib import messages

def registrar_cita(request):
    servicios_destacados = Servicio.objects.all()
    servicios_otros = Servicio.objects.all()

    if request.method == "POST":
        paciente_form = PacienteForm(request.POST)
        cita_form = CitaForm(request.POST)

        # ✅ Mostrar errores en pantalla
        if not paciente_form.is_valid() or not cita_form.is_valid():
            messages.error(request, "❌ Hay errores en el formulario. Revisa los campos.")
            print("ERRORES PACIENTE:", paciente_form.errors)
            print("ERRORES CITA:", cita_form.errors)

        if paciente_form.is_valid() and cita_form.is_valid():
            paciente = paciente_form.save()

            cita = cita_form.save(commit=False)
            cita.paciente = paciente
            cita.save()

            messages.success(request, "✅ Cita registrada correctamente.")
            return redirect('citas')

    else:
        paciente_form = PacienteForm()
        cita_form = CitaForm()

    return render(request, "clinica/registrar_cita.html", {
        "paciente_form": paciente_form,
        "cita_form": cita_form,
        "servicios_destacados": servicios_destacados,
        "servicios_otros": servicios_otros,
        "selected_servicio": None
    })
