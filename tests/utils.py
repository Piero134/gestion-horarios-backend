from datetime import date, timedelta, time

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from asignaturas.models import Asignatura, Equivalencia
from aulas.models import Aula
from docentes.models import Docente
from escuelas.models import Escuela
from facultades.models import Departamento, Facultad
from grupos.models import Grupo
from horarios.models import Horario
from periodos.models import PeriodoAcademico
from planes.models import PlanEstudios


class BaseDataMixin:
    password = "ClaveSegura123"

    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.facultad = Facultad.objects.create(
            nombre="Ingenieria de Sistemas e Informatica",
            siglas="FISI",
            codigo=10,
        )
        cls.otra_facultad = Facultad.objects.create(
            nombre="Ingenieria Industrial",
            siglas="FII",
            codigo=20,
        )
        cls.departamento = Departamento.objects.create(
            nombre="Ciencias de la Computacion",
            facultad=cls.facultad,
        )
        cls.escuela = Escuela.objects.create(
            facultad=cls.facultad,
            nombre="Ingenieria de Sistemas",
        )
        cls.otra_escuela = Escuela.objects.create(
            facultad=cls.facultad,
            nombre="Ingenieria de Software",
        )
        cls.escuela_externa = Escuela.objects.create(
            facultad=cls.otra_facultad,
            nombre="Ingenieria Industrial",
        )
        cls.rol_secretaria = Group.objects.create(name="Secretaria de Escuela")
        cls.rol_vicedecano = Group.objects.create(name="Vicedecano Académico")
        cls.rol_coordinador = Group.objects.create(name="Coordinador de Estudios Generales")
        cls.periodo_activo = PeriodoAcademico.objects.create(
            nombre="2026-I",
            tipo="SEMESTRE",
            anio=2026,
            fecha_inicio=date.today() - timedelta(days=10),
            fecha_fin=date.today() + timedelta(days=90),
        )
        cls.plan = PlanEstudios.objects.create(anio=2023, escuela=cls.escuela)
        cls.otro_plan = PlanEstudios.objects.create(anio=2023, escuela=cls.otra_escuela)
        cls.plan_externo = PlanEstudios.objects.create(anio=2023, escuela=cls.escuela_externa)
        cls.asignatura = Asignatura.objects.create(
            plan=cls.plan,
            ciclo=3,
            codigo="SI301",
            nombre="Arquitectura de Software",
            creditos=4,
            horas_teoria=2,
            horas_practica=2,
            horas_laboratorio=0,
        )
        cls.asignatura_eg = Asignatura.objects.create(
            plan=cls.plan,
            ciclo=1,
            codigo="EG101",
            nombre="Comunicacion",
            creditos=3,
            horas_teoria=2,
            horas_practica=0,
            horas_laboratorio=0,
        )
        cls.asignatura_externa = Asignatura.objects.create(
            plan=cls.plan_externo,
            ciclo=3,
            codigo="II301",
            nombre="Logistica",
            creditos=4,
            horas_teoria=2,
            horas_practica=0,
            horas_laboratorio=0,
        )
        cls.asignatura_otra_escuela = Asignatura.objects.create(
            plan=cls.otro_plan,
            ciclo=3,
            codigo="SW301",
            nombre="Arquitectura de Software",
            creditos=4,
            horas_teoria=2,
            horas_practica=2,
            horas_laboratorio=0,
        )
        cls.equivalencia = Equivalencia.objects.create(nombre="Arquitectura equivalente")
        cls.equivalencia.asignaturas.add(cls.asignatura, cls.asignatura_otra_escuela)
        cls.grupo = Grupo.objects.create(
            numero=1,
            asignatura=cls.asignatura,
            periodo=cls.periodo_activo,
        )
        cls.grupo_eg = Grupo.objects.create(
            numero=2,
            asignatura=cls.asignatura_eg,
            periodo=cls.periodo_activo,
        )
        cls.docente = Docente.objects.create(
            apellido_paterno="PEREZ",
            apellido_materno="QUISPE",
            nombres="ANA",
            dni="12345678",
            email="ana.perez@example.com",
            tipo=Docente.TipoDocente.NOMBRADO,
            facultad=cls.facultad,
            departamento=cls.departamento,
            codigo="DOC-001",
            categoria=Docente.Categoria.AUXILIAR,
            dedicacion=Docente.Dedicacion.TIEMPO_COMPLETO,
        )
        cls.aula = Aula.objects.create(
            nombre="101",
            pabellon=Aula.Pabellon.NUEVO_PABELLON,
            vacantes=40,
            tipo=Aula.Tipo.AULA,
            facultad=cls.facultad,
        )
        cls.horario = Horario.objects.create(
            grupo=cls.grupo,
            tipo="T",
            dia=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            aula=cls.aula,
            docente=cls.docente,
        )
        cls.user = cls.create_user(
            email="secretaria@example.com",
            rol=cls.rol_secretaria,
            escuela=cls.escuela,
            facultad=cls.facultad,
            first_name="Ada",
        )
        cls.vicedecano = cls.create_user(
            email="vicedecano@example.com",
            rol=cls.rol_vicedecano,
            escuela=None,
            facultad=cls.facultad,
        )
        cls.coordinador = cls.create_user(
            email="coordinador@example.com",
            rol=cls.rol_coordinador,
            escuela=None,
            facultad=cls.facultad,
        )

    @classmethod
    def create_user(cls, email, rol, facultad, escuela=None, **extra_fields):
        return cls.User.objects.create_user(
            email=email,
            password=cls.password,
            rol=rol,
            facultad=facultad,
            escuela=escuela,
            **extra_fields,
        )
