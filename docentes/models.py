from django.db import models
from django.core.exceptions import ValidationError
from facultades.models import Departamento

class Docente(models.Model):
    # --- ENUMS ---
    class TipoDocente(models.TextChoices):
        NOMBRADO = 'N', 'Nombrado'
        CONTRATADO = 'C', 'Contratado'

    class Categoria(models.TextChoices):
        PRINCIPAL = 'PRI', 'Principal'
        ASOCIADO = 'ASO', 'Asociado'
        AUXILIAR = 'AUX', 'Auxiliar'

    class Dedicacion(models.TextChoices):
        DEDICACION_EXCLUSIVA = 'DE', 'Dedicación Exclusiva'
        TIEMPO_COMPLETO = 'TC', 'Tiempo Completo'
        TIEMPO_PARCIAL = 'TP', 'Tiempo Parcial'

    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    nombres = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True)
    email = models.EmailField(verbose_name="Correo Institucional", unique=True, blank=True, null=True)

    tipo = models.CharField(
        max_length=1,
        choices=TipoDocente.choices,
        default=TipoDocente.CONTRATADO
    )

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='docentes'
    )

    codigo = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código Docente",
        help_text="Obligatorio solo para docentes nombrados"
    )

    categoria = models.CharField(
        max_length=3,
        choices=Categoria.choices,
        null=True,
        blank=True
    )

    dedicacion = models.CharField(
        max_length=2,
        choices=Dedicacion.choices,
        null=True,
        blank=True,
        verbose_name="Clase/Dedicación"
    )

    class Meta:
        verbose_name = "Docente"
        verbose_name_plural = "Docentes"
        ordering = ['apellido_paterno', 'apellido_materno', 'nombres']

    def __str__(self):
        return f"{self.apellido_paterno} {self.apellido_materno}, {self.nombres}"

    def clean(self):
        super().clean()

        if self.tipo == self.TipoDocente.NOMBRADO:
            errores = {}
            if not self.codigo:
                errores['codigo'] = "El código es obligatorio para docentes nombrados."
            if not self.categoria:
                errores['categoria'] = "La categoría es obligatoria para docentes nombrados."
            if not self.dedicacion:
                errores['dedicacion'] = "La dedicación es obligatoria para docentes nombrados."

            if errores:
                raise ValidationError(errores)
