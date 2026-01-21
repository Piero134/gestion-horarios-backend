from django.db import models

# Create your models here.

class Facultad(models.Model):
    nombre = models.CharField(
        max_length=50,
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
        return f"{self.siglas} - {self.nombre}"
