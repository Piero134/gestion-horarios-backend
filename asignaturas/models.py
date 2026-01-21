from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from planes.models import PlanEstudios

class Ciclo(models.Model):
    numero = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        unique=True
    )

    class Meta:
        verbose_name = "Ciclo"
        verbose_name_plural = "Ciclos"
        ordering = ['numero']

    def __str__(self):
        return f"Ciclo {self.numero}"

class Asignatura(models.Model):

    class TipoAsignatura(models.TextChoices):
        OBLIGATORIO = 'O', 'Obligatorio'
        ELECTIVO = 'E', 'Electivo'
        OPTATIVO = 'OP', 'Optativo'
        ALTERNATIVO = 'AL', 'Alternativo'

    plan = models.ForeignKey(
        PlanEstudios,
        on_delete=models.CASCADE,
        related_name='asignaturas'
    )

    ciclo = models.ForeignKey(
        Ciclo,
        on_delete=models.PROTECT,
        related_name='asignaturas'
    )
    
    codigo = models.CharField(
        max_length=20,
        unique=True, # Unico por asignatura
        verbose_name="Código de asignatura"
    )

    tipo = models.CharField(
        max_length=2,
        choices=TipoAsignatura.choices,
        default=TipoAsignatura.OBLIGATORIO,
        verbose_name="Tipo de asignatura"
    )

    nombre = models.CharField(max_length=50)

    creditos = models.PositiveIntegerField()

    prerequisitos = models.ManyToManyField(
        'self',
        through='Prerequisito',
        symmetrical=False,
        related_name='sucesoras',
        blank=True
    )

    horas_teoria = models.PositiveSmallIntegerField(default=0)
    horas_practica = models.PositiveSmallIntegerField(default=0)
    horas_laboratorio = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
        unique_together = ('codigo', 'plan')
        ordering = ['ciclo__numero', 'codigo']

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
        verbose_name = "Prerrequisito"
        verbose_name_plural = "Prerrequisitos"

    def clean(self):
        if not self.asignatura_id or not self.prerequisito_id:
            return

        # No puede ser ella misma
        if self.asignatura == self.prerequisito:
            raise ValidationError(
                "Una asignatura no puede ser prerrequisito de sí misma."
            )

        # El prerrequisito debe ser de un ciclo menor
        if self.prerequisito.ciclo.numero >= self.asignatura.ciclo.numero:
            raise ValidationError(
                "El prerrequisito debe pertenecer a un ciclo anterior."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prerequisito.nombre} → {self.asignatura.nombre}"
