import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_horarios.settings')
django.setup()

from horarios.exporters import (
    generar_reporte_grupos,
    generar_reporte_por_asignatura,
    generar_reporte_matricula
)
from grupos.models import Grupo
from periodos.models import PeriodoAcademico

def test_exportacion():
    print("=" * 60)
    print("PRUEBA DE EXPORTACIÓN DE REPORTES EXCEL")
    print("=" * 60)
    
    # Verificar que hay datos
    total_grupos = Grupo.objects.count()
    if total_grupos == 0:
        print("\nNo hay grupos en la base de datos.")
        print("   Ejecuta primero: python test_import.py")
        return
    
    print(f"\nDatos disponibles:")
    print(f"   Grupos en BD: {total_grupos}")
    print(f"   Periodos en BD: {PeriodoAcademico.objects.count()}")
    
    try:
        # Reporte 1: Grupos
        print("\n   1. Reporte de grupos (grilla semanal)...", end=" ")
        generar_reporte_grupos(archivo_salida='test_reporte_grupos.xlsx')
        print("✅")
        print("      Archivo: test_reporte_grupos.xlsx")
        
        # Reporte 2: Asignaturas
        print("\n   2. Reporte por asignatura y ciclo...", end=" ")
        generar_reporte_por_asignatura(archivo_salida='test_reporte_asignaturas.xlsx')
        print("✅")
        print("      Archivo: test_reporte_asignaturas.xlsx")
        
        # Reporte 3: Matrícula
        print("\n   3. Reporte de matrícula...", end=" ")
        generar_reporte_matricula(archivo_salida='test_reporte_matricula.xlsx')
        print("✅")
        print("      Archivo: test_reporte_matricula.xlsx")
        
        print("\n" + "=" * 60)
        print("✅ REPORTES GENERADOS EXITOSAMENTE")
        print("=" * 60)
        print("\nArchivos creados:")
        print("  1. test_reporte_grupos.xlsx")
        print("  2. test_reporte_asignaturas.xlsx")
        print("  3. test_reporte_matricula.xlsx")
        
        # Verificar tamaños
        print("\nTamaños de archivos:")
        for archivo in ['test_reporte_grupos.xlsx', 'test_reporte_asignaturas.xlsx', 'test_reporte_matricula.xlsx']:
            if os.path.exists(archivo):
                size_kb = os.path.getsize(archivo) / 1024
                print(f"  {archivo}: {size_kb:.1f} KB")
        
    except Exception as e:
        print(f"\n❌ Error generando reportes:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_exportacion()
