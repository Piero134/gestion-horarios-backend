from django.shortcuts import render
import pandas as pd

# Create your views here.
def cargarExcel(nameExcel):
    df=pd.read_excel(nameExcel,usecols=[1,2,3,4,5,6],header=None)
    df.fillna(0,inplace=True)

    for index, fila in df.iterrows():
        curso=fila[1]
        grupo=fila[2]
        tipo_clase=fila[3]
        dia=fila[4]
        hora_inicio=fila[5]
        hora_fin=fila[6]
        
        return
        

cargarExcel('excel.xlsx')