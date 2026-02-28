from django.db import models

# Create your models here.

class Facultad(models.Model):
    nombre = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nombre"
    )

    siglas = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Siglas"
    )

    codigo = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name="Código"
    )

    class Meta:
        verbose_name = "Facultad"
        verbose_name_plural = "Facultades"
        ordering = ['codigo']

    def __str__(self):
        return f"Facultad de {self.nombre}"


class Departamento(models.Model):
    nombre = models.CharField(max_length=50)
    facultad = models.ForeignKey(
        Facultad,
        on_delete=models.CASCADE,
        related_name='departamentos'
    )

    class Meta:
        unique_together = ('facultad', 'nombre')
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"

    def __str__(self):
        return f"{self.nombre}"
