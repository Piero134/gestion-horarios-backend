from django.db import models
from facultades.models import Facultad
from django.core.validators import MinValueValidator

class Aula(models.Model):
    class Pabellon(models.TextChoices):
        ANTIGUO_PABELLON = 'AP', 'Antiguo Pabellón'
        NUEVO_PABELLON = 'NP', 'Nuevo Pabellón'

    class Tipo(models.TextChoices):
        AULA = 'A', 'Aula'
        LABORATORIO = 'L', 'Laboratorio'

    nombre = models.CharField(
        max_length=20,
        verbose_name="Nombre del Aula",
        help_text="Ej: 101 NP, 203 AP, LAB 2"
    )

    pabellon = models.CharField(
        max_length=3,
        choices=Pabellon.choices,
        verbose_name="Pabellón"
    )

    vacantes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Vacantes",
        help_text="Capacidad máxima de alumnos"
    )

    tipo = models.CharField(
        max_length=1,
        choices=Tipo.choices,
        default=Tipo.AULA,
        verbose_name="Tipo de Aula",
    )

    facultad = models.ForeignKey(
        Facultad,
        on_delete=models.CASCADE,
        related_name='aulas',
        verbose_name="Facultad",
        help_text="Facultad a la que pertenece el aula"
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el aula está disponible en el sistema"
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('nombre', 'pabellon')
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"
        ordering = ['pabellon', 'nombre']

    def __str__(self):
        return f"{self.get_tipo_display()} {self.nombre}-{self.pabellon}"

    @property
    def es_aula(self):
        """Indica si el aula es de tipo Aula."""
        return self.tipo == self.Tipo.AULA

    @property
    def es_laboratorio(self):
        """Indica si el aula es de tipo Laboratorio."""
        return self.tipo == self.Tipo.LABORATORIO
