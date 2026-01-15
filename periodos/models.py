from django.db import models
from django.core.exceptions import ValidationError

class PeriodoAcademico(models.Model):
    TIPO_CHOICES = [
        ('SEMESTRE', 'Semestre'),
        ('ANUAL', 'Anual'),
        ('VERANO', 'Cursos de Verano'),
    ]

    nombre = models.CharField(
        max_length=20,
        unique=True
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='SEMESTRE'
    )
    anio = models.PositiveSmallIntegerField(verbose_name="Año")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    @property
    def activo(self):
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_fin

    class Meta:
        verbose_name = "Periodo Académico"
        verbose_name_plural = "Periodos Académicos"
        ordering = ['-anio', '-fecha_inicio']

    def clean(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio >= self.fecha_fin:
                raise ValidationError("La fecha de inicio debe ser anterior a la de fin.")

    def __str__(self):
        return self.nombre
