import os
import pandas as pd
import numpy as np
from django.conf import settings

DATASETS_DIR = os.path.join(settings.MEDIA_ROOT, 'datasets')

def guardar_dataset(archivo):
    os.makedirs(DATASETS_DIR, exist_ok=True)
    ruta = os.path.join(DATASETS_DIR, archivo.name)
    with open(ruta, 'wb+') as destino:
        for chunk in archivo.chunks():
            destino.write(chunk)
    return archivo.name

def listar_datasets():
    if not os.path.exists(DATASETS_DIR):
        return []
    return sorted([f for f in os.listdir(DATASETS_DIR) if f.endswith(('.csv', '.xlsx', '.xls'))])

def leer_archivo_df(nombre_archivo):
    if not nombre_archivo:
        return None
    ruta = os.path.join(DATASETS_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return None
    
    if nombre_archivo.endswith(('.xlsx', '.xls')):
        return pd.read_excel(ruta)

    # Prueba combinaciones de codificación y separador típicas de portales argentinos
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        for sep in [',', ';', '\t']:
            try:
                df = pd.read_csv(ruta, encoding=enc, sep=sep)
                if df.shape[1] > 1 and len(df) > 0:
                    return df
            except Exception:
                continue
    return None

def obtener_df_filtrado(request):
    disponibles = listar_datasets()
    activo = request.session.get('dataset_activo')
    if not activo or activo not in disponibles:
        activo = disponibles[0] if disponibles else None
        if activo:
            request.session['dataset_activo'] = activo

    df = leer_archivo_df(activo)
    if df is None:
        return None, None, disponibles, {}

    # Extraer opciones disponibles para los controles de filtro
    filtros_meta = {
        'tiene_edad': 'edad' in df.columns and pd.api.types.is_numeric_dtype(df['edad']),
        'edad_min_pob': int(df['edad'].min()) if 'edad' in df.columns and pd.api.types.is_numeric_dtype(df['edad']) else 0,
        'edad_max_pob': int(df['edad'].max()) if 'edad' in df.columns and pd.api.types.is_numeric_dtype(df['edad']) else 100,
        'tiene_sexo': 'sexo' in df.columns,
        'sexos': sorted(df['sexo'].dropna().unique().tolist()) if 'sexo' in df.columns else [],
        'tiene_ministerio': 'ministerio' in df.columns,
        'ministerios': sorted(df['ministerio'].dropna().unique().tolist()) if 'ministerio' in df.columns else [],
    }

    # Aplicar filtros ingresados por el usuario vía GET
    df_filtrado = df.copy()
    edad_min = request.GET.get('edad_min')
    edad_max = request.GET.get('edad_max')
    sexo_sel = request.GET.get('sexo_filtro')
    min_sel = request.GET.get('ministerio_filtro')

    if filtros_meta['tiene_edad']:
        if edad_min and edad_min.isdigit():
            df_filtrado = df_filtrado[df_filtrado['edad'] >= int(edad_min)]
        if edad_max and edad_max.isdigit():
            df_filtrado = df_filtrado[df_filtrado['edad'] <= int(edad_max)]

    if filtros_meta['tiene_sexo'] and sexo_sel and sexo_sel != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['sexo'] == sexo_sel]

    if filtros_meta['tiene_ministerio'] and min_sel and min_sel != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['ministerio'] == min_sel]

    filtros_meta['valores_actuales'] = {
        'edad_min': edad_min or filtros_meta['edad_min_pob'],
        'edad_max': edad_max or filtros_meta['edad_max_pob'],
        'sexo_filtro': sexo_sel or 'TODOS',
        'ministerio_filtro': min_sel or 'TODOS',
        'registros_filtrados': len(df_filtrado),
        'registros_totales': len(df),
    }

    return df_filtrado, activo, disponibles, filtros_meta