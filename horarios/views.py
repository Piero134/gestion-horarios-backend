from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Horario
from .serializers import ClaseSerializer

class api_horarios(APIView):
    """
    API que agrupa todos los horarios por el número de grupo (sección),
    generando una estructura jerárquica de Grupo -> Días -> Clases.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # 1. Traemos TODOS los horarios optimizados en una sola consulta a la BD
        horarios = Horario.objects.select_related(
            'grupo', 'grupo__asignatura', 'aula', 'docente'
        ).order_by('dia', 'hora_inicio')

        # 2. Diccionario temporal para agrupar todo por el número de grupo
        agrupado = {}

        for h in horarios:
            # Usamos el número del grupo como llave (ej. "1", "2")
            num_grupo = str(h.grupo.numero)

            # Si el grupo es nuevo en el bucle, le pre-creamos los 7 días vacíos
            if num_grupo not in agrupado:
                agrupado[num_grupo] = {dia_id: [] for dia_id, _ in Horario.DIAS_CHOICES}

            # Serializamos la clase y la metemos en el día que le corresponde
            clase_data = ClaseSerializer(h).data
            agrupado[num_grupo][h.dia].append(clase_data)

        # 3. Formateamos el resultado final para que coincida exactamente con tu JSON
        dias_mapping = dict(Horario.DIAS_CHOICES)
        resultado = []

        for num_grupo, dias_dict in agrupado.items():
            lista_dias = []
            
            # Iteramos del 1 al 7 para asegurar que los días salgan en orden (Lunes a Domingo)
            for dia_id in range(1, 8):
                clases = dias_dict.get(dia_id, [])
                if clases:  # Solo incluimos el día si tiene clases programadas
                    lista_dias.append({
                        "dia": dias_mapping[dia_id],
                        "clases": clases
                    })

            # Si el grupo tiene al menos un día con clases, lo agregamos al JSON final
            if lista_dias:
                resultado.append({
                    "grupo": num_grupo,
                    "horarios": [
                        {
                            "dias": lista_dias
                        }
                    ]
                })

        # Opcional: Ordenar la lista final por número de grupo para que el "1" siempre salga primero
        resultado.sort(key=lambda x: int(x['grupo']))

        return Response(resultado)