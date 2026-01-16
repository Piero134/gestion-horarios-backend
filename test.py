import pandas as pd
print("Hi! This is a test about how to read excel documents")
df = pd.read_excel('excel.xlsx',usecols=[1,2,3,4,5,6],header=None)

grupos=[]
dias=['lunes','martes','miercoles','jueves','viernes','sabado']

print(df.columns)
asignaturas=df[1].tolist()
conjuntoAsignaturas=set(asignaturas)

grupos=df[2].tolist()
grupos=set(grupos)
print(grupos)

for index, fila in df.iterrows():
    dato1=fila[1]
    dato2=fila[2]

    if dato2 != 'G1':
        print(f"ALERTA: El producto '{dato1}' pertenece a {dato2} . (Fila {index})")
    else:
        print(f"Producto: {dato1} - Stock OK")



