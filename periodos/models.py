from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class PeriodoManager(models.Manager):
    def get_activo(self):
        hoy = timezone.now().date()
        try:
            return self.get(fecha_inicio__lte=hoy, fecha_fin__gte=hoy)
        except self.model.DoesNotExist:
            return None
        except self.model.MultipleObjectsReturned:
            return self.filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy).last()

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

    fuente = models.URLField(blank=True, null=True, help_text="Link a la resolución o página web")

    objects = PeriodoManager()

    class Meta:
        verbose_name = "Periodo Académico"
        verbose_name_plural = "Periodos Académicos"
        ordering = ['-anio', '-fecha_inicio']

    def __str__(self):
        return self.nombre

    @property
    def activo(self):
        hoy = timezone.now().date()
        if self.fecha_inicio and self.fecha_fin:
            return self.fecha_inicio <= hoy <= self.fecha_fin
        return False

    def clean(self):
        super().clean()

        if not self.fecha_inicio or not self.fecha_fin:
            return

        if self.fecha_inicio >= self.fecha_fin:
            raise ValidationError({
                'fecha_fin': "La fecha de finalización debe ser posterior al inicio."
            })

        overlapping = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=self.fecha_fin,
            fecha_fin__gte=self.fecha_inicio
        ).exclude(pk=self.pk)

        if overlapping.exists():
            periodo_choque = overlapping.first()
            raise ValidationError(
                f"Las fechas se solapan con el periodo '{periodo_choque.nombre}' "
                f"({periodo_choque.fecha_inicio} - {periodo_choque.fecha_fin})."
            )
