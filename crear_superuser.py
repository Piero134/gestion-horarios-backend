import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_horarios.settings')
django.setup()

from django.contrib.auth import get_user_model
from facultades.models import Facultad # Asegúrate de que el nombre de la app sea correcto

def create_admin():
    User = get_user_model()
    username = os.getenv('ADMIN_USERNAME')
    email = os.getenv('ADMIN_EMAIL')
    password = os.getenv('ADMIN_PASSWORD')

    if not User.objects.filter(username=username).exists():
        # Buscamos la primera facultad disponible (cargada previamente por cargar_facultades)
        facultad_obj = Facultad.objects.first()
        
        if not facultad_obj:
            print("ERROR: No se encontró ninguna facultad en la base de datos.")
            return

        print(f"Creando superusuario: {username} asignado a {facultad_obj.nombre}...")
        
        # Pasamos la facultad en extra_fields (create_superuser acepta kwargs)
        User.objects.create_superuser(
            username=username, 
            email=email, 
            password=password,
            facultad=facultad_obj # Asignamos el objeto facultad
        )
        print("Superusuario creado con éxito.")
    else:
        print(f"El superusuario '{username}' ya existe.")

if __name__ == '__main__':
    create_admin()