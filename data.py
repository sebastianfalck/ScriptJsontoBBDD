import csv
import json
import sys

# Ruta del archivo CSV
archivo_csv = "ProjectsJenkinsCardifCSV.csv"

# Abrir y leer el archivo CSV
def buscarProyecto(nombreProyecto, namespace, archivoExcel):
    data = []
    with open(archivoExcel, mode='r', encoding='utf-8-sig') as archivo:
        lector_csv = csv.DictReader(archivo, delimiter=";")
        # Iterar sobre las filas del archivo CSV
        for fila in lector_csv:
            fila_limpia = {clave.strip(): valor.strip('[]') for clave, valor in fila.items()}

            # Validar que el proyecto coincida
            if fila_limpia.get('appName') == nombreProyecto:
                # Revisar si el namespace está en alguna de las columnas (si no existe la columna, ignora)
                if any(namespace == fila_limpia.get(col, "") for col in ["NameSpaceDev", "NameSpaceUat", "NameSpacePrd", "NameSpaceDrs"]):
                    data.append(fila_limpia)

    if data:
        return json.dumps(data, ensure_ascii=False, indent=4)
    else:
        return "No_Data"


# Parámetros desde la línea de comandos
nombreProyecto = sys.argv[1]
namespace = sys.argv[2]   # <-- nuevo parámetro
resultadoJson = buscarProyecto(nombreProyecto, namespace, archivo_csv)
print(resultadoJson)