from django.db import models


class Aula(models.Model):
    class Pabellon(models.TextChoices):
        ANTIGUO_PABELLON = 'AP', 'Antiguo Pabellón'
        NUEVO_PABELLON = 'NP', 'Nuevo Pabellón'
        LABORATORIOS = 'LAB', 'Pabellón de Laboratorios'

    class TipoSesion(models.TextChoices):
        TEORIA = 'T', 'Teoría'
        PRÁCTICA = 'P', 'Práctica'
        LABORATORIO = 'L', 'Laboratorio'
        
    nombre = models.CharField(
        max_length=20,
        unique=True,
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
        help_text="Capacidad máxima de alumnos"
    )

    tipo_sesion = models.CharField(
        max_length=1,
        choices=TipoSesion.choices,
        default=TipoSesion.TEORIA,
        verbose_name="Tipo de Sesión",
        help_text="Define si el aula es para Teoría, Práctica o Laboratorio"
    )

    descripcion = models.TextField(
        default="Sin asignar",
        blank=True,
        verbose_name="Descripción"
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el aula está disponible en el sistema"
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"
        ordering = ['pabellon', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_sesion_display()} ({self.vacantes} vacantes)"

    @property
    def es_teoria(self):
        """Indica si el aula es de tipo Teoría."""
        return self.tipo_sesion == self.TipoSesion.TEORIA

    @property
    def es_practica(self):
        """Indica si el aula es de tipo Práctica."""
        return self.tipo_sesion == self.TipoSesion.PRÁCTICA

    @property
    def es_laboratorio(self):
        """Indica si el aula es de tipo Laboratorio."""
        return self.tipo_sesion == self.TipoSesion.LABORATORIO
