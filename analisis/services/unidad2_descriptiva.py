import numpy as np
import pandas as pd

def procesar_unidad2(df: pd.DataFrame, col_num: str = None, col_cat: str = None):
    cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
    cols_cat = df.select_dtypes(exclude=[np.number]).columns.tolist()

    if not col_num or col_num not in cols_num:
        col_num = 'edad' if 'edad' in cols_num else (cols_num[0] if cols_num else None)
    if not col_cat or col_cat not in cols_cat:
        col_cat = 'sexo' if 'sexo' in cols_cat else (cols_cat[0] if cols_cat else None)

    stats_num = {}
    chart_hist = {}
    chart_box = {}
    if col_num:
        serie = df[col_num].dropna()
        q1 = float(serie.quantile(0.25))
        mediana = float(serie.median())
        q3 = float(serie.quantile(0.75))
        ric = q3 - q1
        lim_inf = q1 - 1.5 * ric
        lim_sup = q3 + 1.5 * ric
        outliers = serie[(serie < lim_inf) | (serie > lim_sup)]

        media = float(serie.mean())
        std = float(serie.std())
        cv = (std / media * 100) if media != 0 else 0

        stats_num = {
            'variable': col_num,
            'n': int(len(serie)),
            'media': round(media, 2),
            'mediana': round(mediana, 2),
            'moda': round(float(serie.mode().iloc[0]), 2) if not serie.mode().empty else None,
            'min': round(float(serie.min()), 2),
            'max': round(float(serie.max()), 2),
            'rango': round(float(serie.max() - serie.min()), 2),
            'varianza': round(float(serie.var()), 2),
            'std': round(std, 2),
            'cv': round(cv, 2),
            'q1': round(q1, 2),
            'q3': round(q3, 2),
            'ric': round(ric, 2),
            'asimetria': round(float(serie.skew()), 3),
            'outliers_count': int(len(outliers)),
            'lim_inf': round(lim_inf, 2),
            'lim_sup': round(lim_sup, 2),
        }

        # Datos para Histograma y Ojiva (Frecuencia Acumulada)
        counts, bin_edges = np.histogram(serie, bins=10)
        labels_bins = [f"{round(bin_edges[i],1)}-{round(bin_edges[i+1],1)}" for i in range(len(counts))]
        acumulada = np.cumsum(counts) / len(serie) * 100
        chart_hist = {
            'labels': labels_bins,
            'frecuencias': counts.tolist(),
            'ojiva': [round(x, 2) for x in acumulada.tolist()]
        }
        chart_box = {
            'min': stats_num['min'], 'q1': stats_num['q1'],
            'mediana': stats_num['mediana'], 'q3': stats_num['q3'], 'max': stats_num['max']
        }

    tabla_cat = []
    chart_cat = {}
    if col_cat:
        vc = df[col_cat].fillna('Sin Dato').value_counts().head(12)
        total = len(df)
        acum = 0
        for cat, freq in vc.items():
            rel = (freq / total) * 100
            acum += rel
            tabla_cat.append({
                'categoria': str(cat),
                'fi': int(freq),
                'fr': round(rel, 2),
                'fa': round(acum, 2)
            })
        chart_cat = {
            'labels': [x['categoria'] for x in tabla_cat],
            'values': [x['fi'] for x in tabla_cat]
        }

    return {
        'cols_num': cols_num,
        'cols_cat': cols_cat,
        'col_num_sel': col_num,
        'col_cat_sel': col_cat,
        'stats_num': stats_num,
        'tabla_cat': tabla_cat,
        'chart_hist': chart_hist,
        'chart_box': chart_box,
        'chart_cat': chart_cat,
    }