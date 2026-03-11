from django.db import models
from facultades.models import Facultad


class Aula(models.Model):
    class Pabellon(models.TextChoices):
        ANTIGUO_PABELLON = 'AP', 'Antiguo Pabellón'
        NUEVO_PABELLON = 'NP', 'Nuevo Pabellón'

    class TipoSesion(models.TextChoices):
        TEORIA = 'T', 'Teoría'
        PRACTICA = 'P', 'Práctica'

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
        verbose_name="Vacantes",
        help_text="Capacidad máxima de alumnos",
        default=0
    )

    tipo_sesion = models.CharField(
        max_length=1,
        choices=TipoSesion.choices,
        default=TipoSesion.TEORIA,
        verbose_name="Tipo de Sesión",
        help_text="Define si el aula es para Teoría o Práctica"
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
        return f"{self.nombre} - {self.pabellon}"

    @property
    def es_teoria(self):
        """Indica si el aula es de tipo Teoría."""
        return self.tipo_sesion == self.TipoSesion.TEORIA

    @property
    def es_practica(self):
        """Indica si el aula es de tipo Práctica."""
        return self.tipo_sesion == self.TipoSesion.PRACTICA

    @property
    def es_laboratorio(self):
        """Indica si el aula es de tipo Laboratorio (sesiones prácticas se realizan en laboratorios)."""
        return self.tipo_sesion == self.TipoSesion.PRACTICA

