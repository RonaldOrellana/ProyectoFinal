# Clínica Moderna - Proyecto Django

## Qué contiene
Proyecto Django mínimo listo para ejecutar con una app `clinica` que incluye:
- Modelos: Paciente, Medico, Servicio, Cita
- Vistas y plantillas básicas
- Panel de administración configurado
- Archivos estáticos (CSS)

## Instrucciones rápidas
1. Crear y activar un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate    # Windows
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Migrar y crear superusuario:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```
4. Ejecutar servidor:
   ```bash
   python manage.py runserver
   ```
Visita http://127.0.0.1:8000 y http://127.0.0.1:8000/admin
