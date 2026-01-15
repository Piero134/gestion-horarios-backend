from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from planes.models import PlanEstudios

class Asignatura(models.Model):
    TIPO_ASIGNATURA_CHOICES = [
        ('O', 'Obligatorio'),
        ('E', 'Electivo'),
        ('OP', 'Optativo'),
        ('AL', 'Alternativo'),
    ]

    codigo = models.CharField(
        max_length=20,
        unique=True, # Unico por asignatura
        verbose_name="Código de asignatura"
    )
    tipo = models.CharField(
        max_length=2,
        choices=TIPO_ASIGNATURA_CHOICES,
        default='O',
        verbose_name="Tipo de asignatura"
    )
    nombre = models.CharField(max_length=100)
    creditos = models.PositiveIntegerField()
    ciclo = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    plan = models.ForeignKey(
        PlanEstudios, on_delete=models.CASCADE, related_name='asignaturas'
    )

    prerequisitos = models.ManyToManyField(
        'self',
        through='Prerequisito',
        symmetrical=False,
        related_name='sucesoras'
    )

    class Meta:
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
        unique_together = ('codigo', 'plan')
        ordering = ['ciclo', 'codigo']

    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"

# Tabla intermedia para prerequisitos
class Prerequisito(models.Model):
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='prerequisitos_set'
    )
    prerequisito = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='sucesoras_set'
    )

    class Meta:
        unique_together = ('asignatura', 'prerequisito')

    def clean(self):
        # El prerrequisito no puede ser de un ciclo mayor a la asignatura
        if self.prerequisito.ciclo > self.asignatura.ciclo:
            raise ValidationError("El prerrequisito no puede ser de un ciclo mayor a la asignatura.")

        # Una asignatura no puede ser requisito de sí misma
        if self.asignatura == self.prerequisito:
            raise ValidationError("Una asignatura no puede ser requisito de sí misma.")

    def __str__(self):
        return f"{self.prerequisito.codigo} es requisito de {self.asignatura.codigo}"
