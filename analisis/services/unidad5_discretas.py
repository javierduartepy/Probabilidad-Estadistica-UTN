import numpy as np
import pandas as pd
from scipy import stats

def procesar_unidad5(df: pd.DataFrame, n_ensayos: int = 10, n_sim: int = 10000):
    # Probabilidad empírica de éxito p desde el dataset (ej. proporción de mujeres 'F' o primera categoría)
    if 'sexo' in df.columns:
        p_emp = float((df['sexo'] == 'F').mean())
        evento_desc = "Funcionario de sexo Femenino (F)"
    else:
        col0 = df.select_dtypes(exclude=[np.number]).columns[0]
        val0 = df[col0].mode()[0]
        p_emp = float((df[col0] == val0).mean())
        evento_desc = f"{col0} == {val0}"

    # Modelo Binomial B(n_ensayos, p_emp)
    ks = list(range(0, n_ensayos + 1))
    prob_teorica = [float(stats.binom.pmf(k, n_ensayos, p_emp)) for k in ks]

    # Simulación de 10.000 repeticiones en NumPy
    rng = np.random.default_rng(42)
    simulados = rng.binomial(n_ensayos, p_emp, size=n_sim)
    conteos = np.bincount(simulados, minlength=n_ensayos + 1)
    freq_empirica = (conteos / n_sim).tolist()

    # Modelo Poisson equivalente (lambda = n * p)
    lam = n_ensayos * p_emp
    prob_poisson = [float(stats.poisson.pmf(k, lam)) for k in ks]

    tabla_comparativa = [
        {
            'k': k,
            'teorica_binom': round(prob_teorica[k], 4),
            'simulada_emp': round(freq_empirica[k], 4),
            'teorica_poisson': round(prob_poisson[k], 4),
            'diff_abs': round(abs(prob_teorica[k] - freq_empirica[k]), 4)
        }
        for k in ks
    ]

    return {
        'evento_desc': evento_desc,
        'p_emp': round(p_emp, 4),
        'n_ensayos': n_ensayos,
        'n_sim': n_sim,
        'esperanza': round(n_ensayos * p_emp, 2),
        'varianza': round(n_ensayos * p_emp * (1 - p_emp), 2),
        'tabla_comparativa': tabla_comparativa,
        'chart_data': {
            'labels': ks,
            'teorica': [round(x, 4) for x in prob_teorica],
            'simulada': [round(x, 4) for x in freq_empirica],
        }
    }