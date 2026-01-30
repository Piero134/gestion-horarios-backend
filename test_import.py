import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_horarios.settings')
django.setup()

from horarios.importers import importar_horarios_desde_excel
from grupos.models import Grupo
from horarios.models import Horario

def test_importacion():
    archivo = 'horarios_ejemplo.xlsx'
    
    # Verificar que existe el archivo
    if not os.path.exists(archivo):
        print(f"❌ No se encontró '{archivo}'")
        print("   Ejecuta primero: python generar_excel_ejemplo.py")
        return
    
    print("=" * 60)
    print("PRUEBA DE IMPORTACIÓN DE EXCEL")
    print("=" * 60)
    
    # Importar
    print(f"\nImportando '{archivo}'...")
    resultado = importar_horarios_desde_excel(archivo)
    
    # Mostrar resultados
    print(f"\n{'✅' if resultado['success'] else '❌'} Resultado:")
    print(f"   Éxito: {resultado['success']}")
    print(f"   Grupos creados: {resultado['grupos_creados']}")
    print(f"   Horarios creados: {resultado['horarios_creados']}")
    print(f"   Periodo: {resultado['periodo']}")
    
    if resultado['errores']:
        print("\nErrores/Advertencias:")
        for error in resultado['errores']:
            print(f"   - {error}")
    
    # Verificar datos en BD
    print("\nVerificando datos en base de datos:")
    total_grupos = Grupo.objects.count()
    total_horarios = Horario.objects.count()
    print(f"   Total grupos en BD: {total_grupos}")
    print(f"   Total horarios en BD: {total_horarios}")
    
    # Mostrar algunos grupos
    if total_grupos > 0:
        print("\nPrimeros 5 grupos importados:")
        for grupo in Grupo.objects.all()[:5]:
            print(f"   - {grupo.nombre}: {grupo.asignatura.nombre}")
            print(f"     Docente: {grupo.docente or 'Sin asignar'}")
            print(f"     Horarios: {grupo.horarios.count()}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_importacion()
