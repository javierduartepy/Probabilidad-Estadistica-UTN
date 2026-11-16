import numpy as np
import pandas as pd
from scipy import stats
from .data_loader import leer_archivo_df

def comparar_datasets(nombre_a: str, nombre_b: str):
    df_a = leer_archivo_df(nombre_a)
    df_b = leer_archivo_df(nombre_b)
    if df_a is None or df_b is None:
        return None

    res = {
        'nombre_a': nombre_a,
        'nombre_b': nombre_b,
        'filas_a': int(df_a.shape[0]),
        'cols_a': int(df_a.shape[1]),
        'filas_b': int(df_b.shape[0]),
        'cols_b': int(df_b.shape[1]),
        'nulos_a': int(df_a.isna().sum().sum()),
        'nulos_b': int(df_b.isna().sum().sum()),
        'cols_comunes': sorted(list(set(df_a.columns).intersection(set(df_b.columns)))),
    }

    # Comparación de edad si existe en ambos
    if 'edad' in df_a.columns and 'edad' in df_b.columns:
        s_a = pd.to_numeric(df_a['edad'], errors='coerce').dropna()
        s_b = pd.to_numeric(df_b['edad'], errors='coerce').dropna()
        t_stat, p_val = stats.ttest_ind(s_a, s_b, equal_var=False)
        res['edad'] = {
            'media_a': round(float(s_a.mean()), 2),
            'media_b': round(float(s_b.mean()), 2),
            'mediana_a': round(float(s_a.median()), 2),
            'mediana_b': round(float(s_b.median()), 2),
            'std_a': round(float(s_a.std()), 2),
            'std_b': round(float(s_b.std()), 2),
            't_stat': round(float(t_stat), 4),
            'p_valor': f"{p_val:.4e}",
            'diferencia_sig': bool(p_val < 0.05)
        }

    # Comparación de distribución por sexo si existe en ambos
    if 'sexo' in df_a.columns and 'sexo' in df_b.columns:
        dist_a = (df_a['sexo'].value_counts(normalize=True) * 100).round(2).to_dict()
        dist_b = (df_b['sexo'].value_counts(normalize=True) * 100).round(2).to_dict()
        categorias = sorted(list(set(dist_a.keys()).union(set(dist_b.keys()))))
        res['sexo'] = {
            'categorias': categorias,
            'pct_a': [dist_a.get(c, 0) for c in categorias],
            'pct_b': [dist_b.get(c, 0) for c in categorias],
        }

    return res