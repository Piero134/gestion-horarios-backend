import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_horarios.settings')
django.setup()

from django.contrib.auth import get_user_model
from facultades.models import Facultad

def create_admin_manual():
    User = get_user_model()
    username = os.environ.get('ADMIN_USERNAME')
    email = os.environ.get('ADMIN_EMAIL')
    password = os.environ.get('ADMIN_PASSWORD')
    
    if not all([username, email, password]):
        print("Error: Variables ADMIN_USERNAME, ADMIN_EMAIL o ADMIN_PASSWORD no encontradas.")
        return

    if not User.objects.filter(username=username).exists():
        print(f"--- Iniciando creación MANUAL de admin para {username} ---")
        
        # 1. Asegurar una facultad
        facultad_instancia = Facultad.objects.first()
        if not facultad_instancia:
            facultad_instancia, _ = Facultad.objects.get_or_create(
                nombre="Facultad de Ingeniería de Sistemas e Informática",
                siglas="FISI"
            )

        try:
            # 2. Crear el usuario como un objeto normal primero
            user = User(
                username=username,
                email=email,
                facultad=facultad_instancia,
                is_staff=True,
                is_superuser=True
            )
            # 3. Encriptar la contraseña manualmente
            user.set_password(password)
            # 4. Guardar
            user.save()
            
            print(f"✔ ¡LOGRADO! Admin creado manualmente y vinculado a {facultad_instancia.nombre}")
            
        except Exception as e:
            print(f"⚠ Error en creación manual: {str(e)}")
    else:
        print(f"El usuario {username} ya existe.")

if __name__ == "__main__":
    create_admin_manual()