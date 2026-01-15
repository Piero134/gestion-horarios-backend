from django.db import models
from django.core.exceptions import ValidationError

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

    grupo = models.ForeignKey(
        'Grupo',
        on_delete=models.CASCADE,
        related_name='horarios'
    )
    dia = models.PositiveSmallIntegerField(choices=DIAS_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.ForeignKey(
        'Aula',
        on_delete=models.PROTECT,
        related_name='horarios'
    )

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ['dia', 'hora_inicio']

    def __str__(self):
        return f"{self.get_dia_display()}: {self.hora_inicio} - {self.hora_fin} ({self.aula.codigo})"

    def clean(self):
        if self.hora_inicio and self.hora_fin:
            # Validar que la hora de inicio sea antes que la hora de fin
            if self.hora_inicio >= self.hora_fin:
                raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

            # Validar cruces en el mismo aula
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
                    f"Conflicto de horario: El aula {self.aula} ya está ocupada en este rango por otro grupo."
                )
