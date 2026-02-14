import os
import django
import sys

# 1. Configuración del entorno Django (CRUCIAL HACERLO PRIMERO)
# Ajusta 'gestion_horarios.settings' si tu carpeta de configuración se llama diferente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_horarios.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente.")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    print("   Asegúrate de estar en la carpeta raíz y que el entorno virtual esté activo.")
    sys.exit(1)

# 2. Importaciones de modelos y lógica (SOLO DESPUÉS DE SETUP)
from horarios.importers import importar_horarios_desde_excel
from grupos.models import Grupo
from horarios.models import Horario
from asignaturas.models import Asignatura
from planes.models import PlanEstudios

def test_importacion():
    archivo = 'horarios_ejemplo.xlsx' 
    
    if not os.path.exists(archivo):
        print(f"❌ No se encontró el archivo: {archivo}")
        return
    
    print("\n" + "="*50)
    print(" INICIANDO IMPORTACIÓN ")
    print("="*50)
    
    try:
        resultado = importar_horarios_desde_excel(archivo)
        
        print("\n📊 RESUMEN:")
        print(f"   Periodo: {resultado['periodo']}")
        print(f"   Grupos creados: {resultado['grupos_creados']}")
        print(f"   Horarios creados: {resultado['horarios_creados']}")
        
        if resultado['errores']:
            print(f"\n⚠️ Se encontraron {len(resultado['errores'])} errores:")
            for err in resultado['errores'][:10]: # Muestra solo los primeros 10
                print(f"   - {err}")
            if len(resultado['errores']) > 10:
                print("   ... (y más)")
        else:
            print("\n✅ Importación limpia sin errores.")

    except Exception as e:
        print(f"\n❌ Error crítico durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

    # 3. Verificación de Datos
    print("\n" + "="*50)
    print(" VERIFICACIÓN DE BASE DE DATOS ")
    print("="*50)
    
    try:
        print(f"Plan de Estudios: {PlanEstudios.objects.count()}")
        print(f"Asignaturas:      {Asignatura.objects.count()}")
        print(f"Grupos:           {Grupo.objects.count()}")
        print(f"Horarios:         {Horario.objects.count()}")
        
        if Grupo.objects.count() > 0:
            print("\n🔍 Ejemplo de dato insertado:")
            g = Grupo.objects.first()
            print(f"   Grupo: {g.nombre}")
            print(f"   Asignatura: {g.asignatura.nombre}")
            print(f"   Docente: {g.docente}")
            print(f"   Horarios count: {g.horarios.count()}")
    except Exception as e:
        print(f"Error verificando datos: {e}")

if __name__ == '__main__':
    test_importacion()