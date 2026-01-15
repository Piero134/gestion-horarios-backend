from django.db import models

class Aula(models.Model):
    codigo = models.CharField(max_length=10, unique=True) # Ej: A-101
    tipo = models.CharField(max_length=20, choices=[('TEORIA', 'Teoría'), ('LAB', 'Laboratorio')])
    capacidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.codigo} ({self.capacidad} vacantes)"
