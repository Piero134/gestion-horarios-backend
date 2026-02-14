from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import datetime
from grupos.models import Grupo

class Horario(models.Model):
    # Dias de la semana
    DIAS_CHOICES = [
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]

    TIPO_CHOICES = [
        ('T', 'Teoría'),
        ('P', 'Práctica'),
        ('L', 'Laboratorio'),
    ]

    grupo = models.ForeignKey(
        'grupos.Grupo',
        on_delete=models.CASCADE,
        related_name='horarios'
    )

    tipo = models.CharField(
        max_length=1,
        choices=TIPO_CHOICES,
        default='T',
        verbose_name="Tipo de sesión"
    )

    dia = models.PositiveSmallIntegerField(choices=DIAS_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.ForeignKey(
        'aulas.Aula',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='horarios'
    )

    docente = models.ForeignKey(
        'docentes.Docente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='horarios_asignados' # Cambiamos el related_name
    )

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ['dia', 'hora_inicio']

    def __str__(self):
        nombre_aula = self.aula.nombre if self.aula else "Sin Aula"
        nombre_docente = self.docente.nombre if self.docente else "Sin Docente"
        return f"{self.get_dia_display()}: {self.hora_inicio} - {self.hora_fin} ({nombre_aula}) - {nombre_docente}"

    def clean(self):
        if not self.hora_inicio or not self.hora_fin:
            return

        if self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

        try:
            if not self.grupo_id:
                return

            grupo = self.grupo
            periodo = grupo.periodo
            asignatura = grupo.asignatura
        except ObjectDoesNotExist:
             return

        if self.aula:
            cruces_aula = Horario.objects.filter(
                aula=self.aula,
                dia=self.dia,
                grupo__periodo=periodo,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio
            )

            if self.pk:
                cruces_aula = cruces_aula.exclude(pk=self.pk)

            if cruces_aula.exists():
                raise ValidationError(
                    f"Conflicto de aula: El aula {self.aula} ya está ocupada en este rango."
                )

        if self.docente:
            cruces_docente = Horario.objects.filter(
                docente=self.docente,
                dia=self.dia,
                grupo__periodo=periodo,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio
            )

            if self.pk:
                cruces_docente = cruces_docente.exclude(pk=self.pk)

            if cruces_docente.exists():
                cruce = cruces_docente.first()
                raise ValidationError({
                    'docente': f"El docente {self.docente} ya tiene clase a esta hora (Grupo {cruce.grupo})."
                })

        horas_requeridas = {
            'T': asignatura.horas_teoria,
            'P': asignatura.horas_practica,
            'L': asignatura.horas_laboratorio,
        }

        fecha_base = datetime.now().date()

        inicio = datetime.combine(fecha_base, self.hora_inicio)
        fin = datetime.combine(fecha_base, self.hora_fin)
        duracion_actual = (fin - inicio).seconds / 3600

        total_por_tipo = {'T': 0, 'P': 0, 'L': 0}

        # Traemos horarios excluyendo el actual
        horarios = grupo.horarios.all()
        if self.pk:
            horarios = horarios.exclude(pk=self.pk)

        for h in horarios:
            if not h.hora_inicio or not h.hora_fin:
                continue

            hi = datetime.combine(fecha_base, h.hora_inicio)
            hf = datetime.combine(fecha_base, h.hora_fin)

            if h.tipo in total_por_tipo:
                total_por_tipo[h.tipo] += (hf - hi).seconds / 3600

        if self.tipo in total_por_tipo:
            total_por_tipo[self.tipo] += duracion_actual

        limite = horas_requeridas.get(self.tipo, 0)

        if round(total_por_tipo[self.tipo], 2) > limite:
            raise ValidationError(
                f"Las horas de {self.get_tipo_display()} ({round(total_por_tipo[self.tipo], 2)}) "
                f"exceden lo permitido para la asignatura ({limite} horas)."
            )
