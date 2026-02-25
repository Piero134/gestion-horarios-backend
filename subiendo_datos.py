# subiendo_datos.py
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from gestion.models import Curso, Grupo, TipoClase, Horario, Ciclo, Docente, Aula
import pandas as pd


# Create your views here.
def cargarExcel(nameExcel):
    df=pd.read_excel(nameExcel,usecols=[0,1,2,3,4,5,6,8,9],header=None)
    print(df.dtypes)
    df.fillna("0",inplace=True)     
    
    Horario.objects.all().delete()

    for index, fila in df.iterrows():

        cargaDeDatos=False

        ciclo=fila[0]
        curso=fila[1]
        grupo=fila[2]
        tipo_clase=fila[3]
        dia=fila[4]
        hora_inicio=fila[5]
        hora_fin=fila[6]
        
        docente=fila[8]
        num_aula=fila[9]
        
        
        
        if grupo=="0" or len(grupo)>2:
            continue
            #No quiero este dato
        else:
            
            if Aula.objects.filter(numero=int(num_aula)).exists():
                pass
            else:
                Aula.objects.create(numero=int(num_aula))


            if Curso.objects.filter(nombre=curso).exists():
                pass
            else:
                ciclo_db, no_existia=Ciclo.objects.get_or_create(numero=int(ciclo))

                Curso.objects.create(nombre=curso,ciclo=ciclo_db)

            
            if Grupo.objects.filter(numero=int(grupo[1])).exists():
                pass
            else:
                Grupo.objects.create(numero=int(grupo[1]))
            

            valores={"T":"Teoria","L":"Laboratorio","P":"Practica"}
            if TipoClase.objects.filter(nombre=valores.get(tipo_clase[1])).exists():
                pass
            else:
                TipoClase.objects.create(nombre=valores.get(tipo_clase[1]))
            
            if Docente.objects.filter(nombre=docente).exists():
                pass
            else:
                Docente.objects.create(nombre=docente)
            

            #Guardando registro de horario
            days_week={"1":"LU",
                       "2":"MA",
                       "3":"MI",
                       "4":"JU",
                       "5":"VI",
                       "6":"SA",
                       }
            if Curso.objects.filter(nombre=curso).exists() and Grupo.objects.filter(numero=int(grupo[1])).exists() and TipoClase.objects.filter(nombre=valores.get(tipo_clase[1])).exists():
                Horario.objects.create(
                    dia_semana=days_week.get(dia[0]),
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,

                    aula=Aula.objects.get(numero=num_aula),
                    curso=Curso.objects.get(nombre=curso),
                    grupo=Grupo.objects.get(numero=int(grupo[1])),
                    tipo_clase=TipoClase.objects.get(nombre=valores.get(tipo_clase[1])),
                    docente=Docente.objects.get(nombre=docente)
                )


            print(f"{ciclo} / {curso} / {grupo} / {docente} / {tipo_clase} / {dia} / {hora_inicio} / {hora_fin} ")

    


cargarExcel('arc.xlsx')