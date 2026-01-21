from django.db import models

class Aula(models.Model):
    nombre = models.CharField(max_length=10, unique=True)  # Ej: A-101
    capacidad = models.PositiveIntegerField()
    es_laboratorio = models.BooleanField(default=False)

    def __str__(self):
        tipo = "LAB" if self.es_laboratorio else "TEORÍA"
        return f"{self.nombre} - {tipo} ({self.capacidad} vacantes)"
