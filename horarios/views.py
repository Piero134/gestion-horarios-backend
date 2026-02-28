from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from horarios.models import Horario
from .serializers import ClaseSerializer

class api_horarios(generics.ListAPIView):
    serializer_class = ClaseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # 1. Traemos todo optimizado de la BD
        queryset = Horario.objects.select_related(
            'grupo', 
            'grupo__asignatura', 
            'grupo__asignatura__plan__escuela', 
            'aula', 
            'docente'
        )

        # 2. Capturamos todos los filtros de la URL
        escuela_nombre = self.request.query_params.get('escuela_nombre', None)
        escuela_codigo = self.request.query_params.get('escuela_codigo', None)
        ciclo_req = self.request.query_params.get('ciclo', None)
        grupo_req = self.request.query_params.get('grupo', None)
        
        # 3. Aplicamos los filtros condicionalmente
        if escuela_nombre:
            # Usamos 'icontains' para que busque coincidencias parciales sin importar mayúsculas/minúsculas
            queryset = queryset.filter(grupo__asignatura__plan__escuela__nombre__icontains=escuela_nombre)
            
        if escuela_codigo:
            queryset = queryset.filter(grupo__asignatura__plan__escuela__codigo=escuela_codigo)
            
        if ciclo_req:
            queryset = queryset.filter(grupo__asignatura__ciclo=ciclo_req)
            
        if grupo_req:
            queryset = queryset.filter(grupo__numero=grupo_req)

        return queryset.order_by('dia', 'hora_inicio')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Diccionario maestro para agrupar por el bloque [Escuela + Ciclo]
        agrupado = {}

        for h in queryset:
            # Validaciones de seguridad
            if not h.grupo or not h.grupo.asignatura or not hasattr(h.grupo.asignatura, 'plan') or not h.grupo.asignatura.plan or not h.grupo.asignatura.plan.escuela:
                continue

            # Extraemos los datos
            escuela = h.grupo.asignatura.plan.escuela
            esc_codigo = str(escuela.codigo)
            esc_nombre = escuela.nombre.upper()
            ciclo_num = str(h.grupo.asignatura.ciclo)
            grupo_num = str(h.grupo.numero)

            # Llave única combinada (Ej: "20.1_1")
            llave_bloque = f"{esc_codigo}_{ciclo_num}"

            # Si el bloque Escuela-Ciclo no existe, lo creamos
            if llave_bloque not in agrupado:
                agrupado[llave_bloque] = {
                    "escuela_nombre": esc_nombre,
                    "escuela_codigo": esc_codigo,
                    "ciclo": ciclo_num,
                    "grupos": {}
                }

            # Si el Grupo no existe, le preparamos los 7 días
            if grupo_num not in agrupado[llave_bloque]["grupos"]:
                agrupado[llave_bloque]["grupos"][grupo_num] = {
                    dia_id: [] for dia_id, _ in Horario.DIAS_CHOICES
                }

            # Damos formato y lo metemos en su día
            clase_data = self.get_serializer(h).data
            agrupado[llave_bloque]["grupos"][grupo_num][h.dia].append(clase_data)

        # Convertimos el diccionario en listas para el JSON
        dias_mapping = dict(Horario.DIAS_CHOICES)
        lista_resultados_completos = []

        for llave_bloque, data_bloque in agrupado.items():
            lista_grupos = []
            
            for grupo_num, dias_dict in data_bloque["grupos"].items():
                lista_dias = []
                
                # De Lunes a Domingo
                for dia_id in range(1, 8):
                    clases = dias_dict.get(dia_id, [])
                    if clases:
                        lista_dias.append({
                            "dia": dias_mapping[dia_id],
                            "clases": clases
                        })
                
                if lista_dias:
                    lista_grupos.append({
                        "grupo": grupo_num,
                        "horarios": [{"dias": lista_dias}]
                    })
            
            # Ordenamos los grupos numéricamente (1, 2, 3...)
            lista_grupos.sort(key=lambda x: int(x["grupo"]))
            
            if lista_grupos:
                lista_resultados_completos.append({
                    "escuela_nombre": data_bloque["escuela_nombre"],
                    "escuela_codigo": data_bloque["escuela_codigo"],
                    "ciclo": data_bloque["ciclo"],
                    "grupos": lista_grupos
                })

        # Ordenamos todo alfabéticamente por escuela y numéricamente por ciclo
        lista_resultados_completos.sort(key=lambda x: (x["escuela_nombre"], int(x["ciclo"])))

        # Retornamos la lista completa.
        return Response(lista_resultados_completos)