from django.db import models
from django.core.exceptions import ValidationError
from asignaturas.models import Asignatura
from periodos.models import PeriodoAcademico

class GrupoManager(models.Manager):
    def actuales(self):
        return self.filter(periodo__activo=True)

class Grupo(models.Model):
    nombre = models.CharField(max_length=20)

    asignatura = models.ForeignKey(
        Asignatura, 
        on_delete=models.CASCADE,
        null=True,
        blank=True, 
        related_name='grupos'
    )
    periodo = models.ForeignKey(
        PeriodoAcademico, 
        on_delete=models.CASCADE,
        null=True,
        blank=True, 
        related_name='grupos'
    )

    docente = models.ForeignKey(
        'docentes.Docente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grupos_asignados'
    )

    objects = GrupoManager()

    class Meta:
        unique_together = ('nombre', 'asignatura', 'periodo')
        verbose_name = "Grupo"
        ordering = ['periodo', 'asignatura', 'nombre']

    def __str__(self):
    # Usamos "getattr" o una validación simple para evitar el AttributeError
        cod = self.asignatura.codigo if self.asignatura else "Sin Código"
        nom = self.nombre if self.nombre else "Sin Nombre"
        per = self.periodo if self.periodo else "Sin Periodo"
        
        return f"{cod} - {nom} ({per})"
