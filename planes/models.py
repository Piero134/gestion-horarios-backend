from django.db import models
from escuelas.models import Escuela

class PlanEstudios(models.Model):
    nombre = models.CharField(max_length=50)  # Plan 2018, Plan 2023
    escuela = models.ForeignKey(
        Escuela, on_delete=models.CASCADE, related_name='planes'
    )

    class Meta:
        unique_together = ('nombre', 'escuela')

    def __str__(self):
        return f"{self.nombre} - {self.escuela}"
    