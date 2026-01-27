from django.db import models
from facultades.models import Facultad

class Escuela(models.Model):
    facultad = models.ForeignKey(
        Facultad,
        on_delete=models.PROTECT,
        related_name='escuelas'
    )
    nombre = models.CharField(max_length=30, unique=True)
    codigo = models.CharField(max_length=6, editable=False, unique=True)

    class Meta:
        verbose_name = "Escuela Profesional"
        verbose_name_plural = "Escuelas Profesionales"
        ordering = ('codigo',)

    def save(self, *args, **kwargs):
        # Solo generar el código si es nueva
        if not self.pk:
            ultimo = (
                Escuela.objects
                .filter(facultad=self.facultad)
                .order_by('-codigo')
                .first()
            )

            if ultimo:
                ultimo_num = int(ultimo.codigo.split('.')[-1])
                siguiente = ultimo_num + 1
            else:
                siguiente = 1

            self.codigo = f"{self.facultad.codigo}.{siguiente}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
