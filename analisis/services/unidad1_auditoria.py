import csv
import pandas as pd

def procesar_unidad1(df: pd.DataFrame, ruta_csv: str):
    # 1. Carga nativa con listas y diccionarios usando la ruta activa
    registros_nativos = []
    with open(ruta_csv, mode='r', encoding='utf-8', errors='replace') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            registros_nativos.append(dict(fila))
    filas, columnas = df.shape
    
    # 2. Auditoría de valores faltantes
    faltantes = df.isna().sum()
    detalle_faltantes = [
        {'variable': col, 'nulos': int(cant), 'porcentaje': round((cant / filas) * 100, 2)}
        for col, cant in faltantes.items() if cant > 0
    ]

    # 3. Duplicados exactos y por identificador (ej. 'cuil' si existe)
    duplicados_exactos = int(df.duplicated().sum())
    col_id = 'cuil' if 'cuil' in df.columns else df.columns[0]
    duplicados_id = int(df[col_id].duplicated().sum())

    # 4. Clasificación de variables y tipos
    diccionario_vars = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        unicos = int(df[col].nunique(dropna=True))
        if 'int' in dtype or 'float' in dtype:
            escala = 'Cuantitativa Discreta' if 'int' in dtype else 'Cuantitativa Continua'
        else:
            escala = 'Identificador / Texto' if unicos > (filas * 0.8) else 'Cualitativa Nominal'
        
        ejemplos = [str(x) for x in df[col].dropna().unique()[:3]]
        diccionario_vars.append({
            'nombre': col,
            'dtype': dtype,
            'escala': escala,
            'unicos': unicos,
            'ejemplos': ', '.join(ejemplos)
        })

    # 5. Control de rangos lógicos (si existe 'edad')
    alerta_edad = None
    if 'edad' in df.columns and pd.api.types.is_numeric_dtype(df['edad']):
        fuera_rango = df[(df['edad'] < 18) | (df['edad'] > 70)]
        alerta_edad = {
            'min': int(df['edad'].min()),
            'max': int(df['edad'].max()),
            'fuera_rango_70': int(len(fuera_rango)),
            'menores_21': int(len(df[df['edad'] < 21]))
        }

    return {
        'n_registros': filas,
        'n_variables': columnas,
        'nativos_count': len(registros_nativos),
        'muestra_nativa': registros_nativos[:5],
        'columnas': list(df.columns),
        'detalle_faltantes': detalle_faltantes,
        'duplicados_exactos': duplicados_exactos,
        'col_id': col_id,
        'duplicados_id': duplicados_id,
        'diccionario_vars': diccionario_vars,
        'alerta_edad': alerta_edad,
    }