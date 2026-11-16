import numpy as np
import pandas as pd
from scipy import stats

def procesar_unidad6(df: pd.DataFrame, col_num: str = None, n_iter: int = 10000):
    cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
    if not col_num or col_num not in cols_num:
        col_num = 'edad' if 'edad' in cols_num else cols_num[0]

    poblacion = df[col_num].dropna().to_numpy()
    mu_pob = float(np.mean(poblacion))
    sigma_pob = float(np.std(poblacion, ddof=1))

    # Ajuste a Normal y Exponencial
    norm_params = stats.norm.fit(poblacion)
    exp_params = stats.expon.fit(poblacion)

    # Simulación del TCL para n = 5, n = 30, n = 100
    rng = np.random.default_rng(42)
    tamanos = [5, 30, 100]
    simulaciones_tcl = {}

    for n in tamanos:
        # Matriz (n_iter, n) de muestreo con reemplazo
        muestras = rng.choice(poblacion, size=(n_iter, n), replace=True)
        medias = muestras.mean(axis=1)
        counts, edges = np.histogram(medias, bins=25, density=True)
        centros = [(edges[i] + edges[i+1]) / 2 for i in range(len(counts))]
        
        # Curva normal teórica según TCL: N(mu, sigma / sqrt(n))
        ee_teorico = sigma_pob / np.sqrt(n)
        curva_tcl = stats.norm.pdf(centros, loc=mu_pob, scale=ee_teorico)

        simulaciones_tcl[f"n_{n}"] = {
            'n': n,
            'media_sim': round(float(np.mean(medias)), 3),
            'ee_sim': round(float(np.std(medias, ddof=1)), 3),
            'ee_teorico': round(float(ee_teorico), 3),
            'labels': [round(c, 2) for c in centros],
            'hist_density': [round(float(h), 4) for h in counts],
            'normal_pdf': [round(float(p), 4) for p in curva_tcl],
        }

    return {
        'cols_num': cols_num,
        'col_sel': col_num,
        'mu_pob': round(mu_pob, 2),
        'sigma_pob': round(sigma_pob, 2),
        'n_iter': n_iter,
        'norm_fit': {'mu': round(norm_params[0], 2), 'sigma': round(norm_params[1], 2)},
        'exp_fit': {'loc': round(exp_params[0], 2), 'scale': round(exp_params[1], 2)},
        'tcl': simulaciones_tcl,
    }