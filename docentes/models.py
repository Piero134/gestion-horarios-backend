from django.db import models
from django.core.exceptions import ValidationError
from facultades.models import Departamento, Facultad

class Docente(models.Model):
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

    facultad = models.ForeignKey(
        Facultad,
        on_delete=models.CASCADE,
        related_name='docentes',
        verbose_name="Facultad de Adscripción"
    )

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='docentes',
        verbose_name="Departamento Académico"
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

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el docente está activo en el sistema"
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Docente"
        verbose_name_plural = "Docentes"
        ordering = ['apellido_paterno', 'apellido_materno', 'nombres']

    def __str__(self):
        return f"{self.apellido_paterno} {self.apellido_materno}, {self.nombres}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"

    @property
    def get_tipo_display(self):
        return self.get_tipo_display()

    def clean(self):
        if self.departamento and self.facultad:
            if self.departamento.facultad != self.facultad:
                raise ValidationError({
                    'departamento': f"El departamento '{self.departamento}' no pertenece a la facultad '{self.facultad}'."
                })

        if self.tipo == self.TipoDocente.NOMBRADO:
            errores = {}
            if not self.departamento:
                errores['departamento'] = "El departamento es obligatorio para docentes nombrados."
            if not self.codigo:
                errores['codigo'] = "El código es obligatorio para docentes nombrados."
            if not self.categoria:
                errores['categoria'] = "La categoría es obligatoria para docentes nombrados."
            if not self.dedicacion:
                errores['dedicacion'] = "La dedicación es obligatoria para docentes nombrados."

            if errores:
                raise ValidationError(errores)

        if self.tipo == self.TipoDocente.CONTRATADO:
            self.departamento = None
            self.codigo = None
            self.categoria = None
            self.dedicacion = None

    def desactivar(self):
        """Desactiva el docente (soft delete)"""
        self.activo = False
        self.save()

    def activar(self):
        """Activa el docente"""
        self.activo = True
        self.save()
