from django.db import models

class Docente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Grupo(models.Model):
    numero = models.IntegerField()

    def __str__(self):
        return f"Grupo {self.numero}"

class Aula(models.Model):
    numero = models.IntegerField()
    piso = models.CharField(max_length=30)
    tipo = models.CharField(max_length=30) # Ej: Laboratorio, Estandar
    estado = models.CharField(max_length=30) # Ej: Disponible, Mantenimiento

    def __str__(self):
        return f"Aula {self.numero} - {self.tipo}"
    
class TipoClase(models.Model):
    nombre = models.CharField(max_length=30) # Ej: Teoría, Laboratorio

    def __str__(self):
        return self.nombre

class Ciclo(models.Model):
    numero = models.IntegerField() # Ej: 1, 2, 3...

    def __str__(self):
        return f"Ciclo {self.numero}"

class TipoCurso(models.Model):
    nombre = models.CharField(max_length=30) # Ej: Obligatoria, Electiva

    def __str__(self):
        return self.nombre

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    creditos = models.IntegerField(blank=True,null=True)
    
    # on_delete=models.PROTECT evita borrar un tipo de curso si hay cursos usándolo
    tipo_curso = models.ForeignKey(TipoCurso, on_delete=models.PROTECT,null=True)
    ciclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f"{self.nombre} ({self.ciclo})"
    
class Horario(models.Model):
    DIAS_OPCIONES = [
        ('LU', 'Lunes'),
        ('MA', 'Martes'),
        ('MI', 'Miércoles'),
        ('JU', 'Jueves'),
        ('VI', 'Viernes'),
        ('SA', 'Sábado'),
    ]

    dia_semana = models.CharField(max_length=2, choices=DIAS_OPCIONES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE,null=True)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE,null=True)
    
    tipo_clase = models.ForeignKey(TipoClase, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.curso.nombre} - {self.dia_semana} ({self.hora_inicio})"