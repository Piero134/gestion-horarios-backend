from django.db import models
from escuelas.models import Escuela
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

def current_year():
    return datetime.date.today().year

class PlanEstudios(models.Model):
    anio = models.PositiveIntegerField(
        verbose_name="Año del Plan",
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2100)
        ],
        help_text="Ingrese el año de vigencia (ej. 2023)"
    )
    escuela = models.ForeignKey(
        Escuela,
        on_delete=models.CASCADE,
        related_name='planes'
    )

    class Meta:
        unique_together = ('anio', 'escuela')
        verbose_name = "Plan de Estudios"
        verbose_name_plural = "Planes de Estudios"
        ordering = ['-anio']

    def __str__(self):
        return f"Plan {self.anio} - {self.escuela}"
