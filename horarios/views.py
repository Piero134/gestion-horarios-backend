from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from horarios.models import Horario
from .serializers import ClaseSerializer

class api_horarios(generics.ListAPIView):
    # Declaramos el uso del ClaseSerializer
    serializer_class = ClaseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # 1. Hacemos la consulta base desde Horario
        queryset = Horario.objects.select_related(
            'grupo', 'grupo__asignatura', 'aula', 'docente'
        )

        # 2. Capturamos SOLO el filtro del grupo desde la URL
        grupo_req = self.request.query_params.get('grupo', None)

        # 3. Filtramos si nos mandan el dato
        if grupo_req:
            queryset = queryset.filter(grupo__numero=grupo_req)

        return queryset.order_by('dia', 'hora_inicio')

    def list(self, request, *args, **kwargs):
        # Obtenemos los horarios ya filtrados solo por grupo
        queryset = self.get_queryset()

        # Rescatamos el valor del grupo de la URL para pintar la cabecera del JSON
        grupo_req = request.query_params.get('grupo', '1')

        # Extraemos el ciclo automáticamente del primer horario encontrado para no romper el JSON
        ciclo_dinamico = ""
        if queryset.exists():
            # Viajamos por la relación: Horario -> Grupo -> Asignatura -> ciclo
            ciclo_dinamico = str(queryset.first().grupo.asignatura.ciclo)

        # Preparamos los días de la semana vacíos
        agrupado_por_dia = {dia_id: [] for dia_id, _ in Horario.DIAS_CHOICES}

        # Iteramos sobre los horarios filtrados
        for h in queryset:
            # Tu ClaseSerializer le da el formato exacto (mayúsculas, aula en 0, etc.)
            clase_data = self.get_serializer(h).data
            agrupado_por_dia[h.dia].append(clase_data)

        # Formateamos el bloque de días usando los nombres reales
        dias_mapping = dict(Horario.DIAS_CHOICES)
        lista_dias = []

        # Iteramos del 1 al 7 para asegurar el orden (Lunes a Domingo)
        for dia_id in range(1, 8):
            clases = agrupado_por_dia.get(dia_id, [])
            if clases:
                lista_dias.append({
                    "dia": dias_mapping[dia_id],
                    "clases": clases
                })

        # Construimos la estructura JSON exacta solicitada
        resultado = {
            "ciclo": ciclo_dinamico, # Se llena solo de forma inteligente
            "grupo": str(grupo_req),
            "horarios": [
                {
                    "dias": lista_dias
                }
            ]
        }

        # Retornamos tu JSON único
        return Response(resultado)