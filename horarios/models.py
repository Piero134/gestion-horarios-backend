from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime

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
        on_delete=models.PROTECT,
        related_name='horarios'
    )

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ['dia', 'hora_inicio']

    def __str__(self):
        return f"{self.get_dia_display()}: {self.hora_inicio} - {self.hora_fin} ({self.aula.nombre})"

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError(
                "La hora de inicio debe ser anterior a la hora de fin."
            )

        # Verificar conflictos de aula
        cruces = Horario.objects.filter(
            aula=self.aula,
            dia=self.dia,
            grupo__periodo=self.grupo.periodo,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio
        )

        if self.pk:
            cruces = cruces.exclude(pk=self.pk)

        if cruces.exists():
            raise ValidationError(
                f"Conflicto de horario: El aula {self.aula} "
                "ya está ocupada en este rango."
            )

        asignatura = self.grupo.asignatura

        horas_requeridas = {
            'T': asignatura.horas_teoria,
            'P': asignatura.horas_practica,
            'L': asignatura.horas_laboratorio,
        }

        # Duración del horario actual
        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        fin = datetime.combine(datetime.today(), self.hora_fin)
        duracion_actual = (fin - inicio).seconds / 3600

        # Sumamos las horas ya existentes del grupo
        total_por_tipo = {'T': 0, 'P': 0, 'L': 0}

        horarios = self.grupo.horarios.all()
        if self.pk:
            horarios = horarios.exclude(pk=self.pk)

        for h in horarios:
            hi = datetime.combine(datetime.today(), h.hora_inicio)
            hf = datetime.combine(datetime.today(), h.hora_fin)
            total_por_tipo[h.tipo] += (hf - hi).seconds / 3600

        # Sumamos el horario actual
        total_por_tipo[self.tipo] += duracion_actual

        # Validamos que no se exceda
        if total_por_tipo[self.tipo] > horas_requeridas[self.tipo]:
            raise ValidationError(
                f"Las horas de {self.get_tipo_display()} exceden lo permitido "
                f"para la asignatura ({horas_requeridas[self.tipo]} horas)."
            )
