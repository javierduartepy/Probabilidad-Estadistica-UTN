import numpy as np
import pandas as pd
from scipy import stats

def procesar_unidad7(df: pd.DataFrame, col_num: str = None):
    cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
    if not col_num or col_num not in cols_num:
        col_num = 'edad' if 'edad' in cols_num else cols_num[0]

    datos = df[col_num].dropna().to_numpy()
    n = len(datos)
    media = float(np.mean(datos))
    ee = float(stats.sem(datos))

    # 1. Intervalos de Confianza Clásicos (90% y 95%)
    ic90_clasico = stats.t.interval(0.90, df=n-1, loc=media, scale=ee)
    ic95_clasico = stats.t.interval(0.95, df=n-1, loc=media, scale=ee)

    # 2. Intervalos de Confianza por Bootstrap (5.000 remuestreos)
    rng = np.random.default_rng(42)
    boot_medias = rng.choice(datos, size=(5000, n), replace=True).mean(axis=1)
    ic90_boot = (float(np.percentile(boot_medias, 5)), float(np.percentile(boot_medias, 95)))
    ic95_boot = (float(np.percentile(boot_medias, 2.5)), float(np.percentile(boot_medias, 97.5)))

    # 3. Prueba de Hipótesis Chi-Cuadrado (Independencia entre dos categóricas, ej. ministerio vs sexo)
    chi2_res = None
    cols_cat = df.select_dtypes(exclude=[np.number]).columns.tolist()
    if 'ministerio' in cols_cat and 'sexo' in cols_cat:
        ct = pd.crosstab(df['ministerio'], df['sexo'])
        chi2, p_val, gl, _ = stats.chi2_contingency(ct)
        chi2_res = {
            'var1': 'ministerio',
            'var2': 'sexo',
            'chi2': round(float(chi2), 3),
            'p_valor': f"{p_val:.4e}",
            'gl': int(gl),
            'rechaza_h0': bool(p_val < 0.05)
        }

    # 4. Correlación y Regresión Lineal Simple (si hay al menos 2 variables numéricas)
    regresion = None
    if len(cols_num) >= 2:
        x_col, y_col = cols_num[0], cols_num[1]
        sub = df[[x_col, y_col]].dropna()
        x = sub[x_col].to_numpy()
        y = sub[y_col].to_numpy()
        res = stats.linregress(x, y)
        cov = float(np.cov(x, y)[0, 1])
        
        # Muestra de puntos para Scatter Plot (máx 150 puntos para fluidez visual)
        idx = np.linspace(0, len(x) - 1, min(150, len(x)), dtype=int)
        regresion = {
            'x_col': x_col,
            'y_col': y_col,
            'pendiente': round(float(res.slope), 4),
            'ordenada': round(float(res.intercept), 4),
            'r_pearson': round(float(res.rvalue), 4),
            'r2': round(float(res.rvalue ** 2), 4),
            'p_valor': f"{res.pvalue:.4e}",
            'covarianza': round(cov, 4),
            'scatter_x': x[idx].tolist(),
            'scatter_y': y[idx].tolist(),
            'linea_y': (res.intercept + res.slope * x[idx]).tolist(),
        }

    return {
        'cols_num': cols_num,
        'col_sel': col_num,
        'media': round(media, 3),
        'ic90_clasico': (round(ic90_clasico[0], 3), round(ic90_clasico[1], 3)),
        'ic95_clasico': (round(ic95_clasico[0], 3), round(ic95_clasico[1], 3)),
        'ic90_boot': (round(ic90_boot[0], 3), round(ic90_boot[1], 3)),
        'ic95_boot': (round(ic95_boot[0], 3), round(ic95_boot[1], 3)),
        'chi2_res': chi2_res,
        'regresion': regresion,
    }