import numpy as np
import pandas as pd
from scipy import stats
from .data_loader import leer_archivo_df

def _buscar_columna_por_palabra(df: pd.DataFrame, palabras_clave: list):
    """Busca cualquier columna cuyo nombre contenga alguna palabra clave (case-insensitive)."""
    for col in df.columns:
        col_limpia = str(col).strip().lower()
        for palabra in palabras_clave:
            if palabra in col_limpia:
                return col
    return None

def comparar_datasets(nombre_a: str, nombre_b: str, filtros: dict = None):
    df_a_orig = leer_archivo_df(nombre_a)
    df_b_orig = leer_archivo_df(nombre_b)
    if df_a_orig is None or df_b_orig is None:
        return None

    filtros = filtros or {}

    col_edad_a = _buscar_columna_por_palabra(df_a_orig, ['edad', 'age'])
    col_edad_b = _buscar_columna_por_palabra(df_b_orig, ['edad', 'age'])
    col_sexo_a = _buscar_columna_por_palabra(df_a_orig, ['sexo', 'genero', 'género'])
    col_sexo_b = _buscar_columna_por_palabra(df_b_orig, ['sexo', 'genero', 'género'])

    tiene_edad = bool(col_edad_a and col_edad_b)
    tiene_sexo = bool(col_sexo_a and col_sexo_b)

    metadatos_comunes = []
    if tiene_edad:
        metadatos_comunes.append(f"Edad ({col_edad_a} / {col_edad_b})")
    if tiene_sexo:
        metadatos_comunes.append(f"Sexo ({col_sexo_a} / {col_sexo_b})")

    df_a = df_a_orig.copy()
    df_b = df_b_orig.copy()

    edad_min_global, edad_max_global = 18, 90
    if tiene_edad:
        df_a['_edad'] = pd.to_numeric(df_a[col_edad_a], errors='coerce')
        df_b['_edad'] = pd.to_numeric(df_b[col_edad_b], errors='coerce')
        ea = df_a['_edad'].dropna()
        eb = df_b['_edad'].dropna()
        if len(ea) and len(eb):
            edad_min_global = int(min(ea.min(), eb.min()))
            edad_max_global = int(max(ea.max(), eb.max()))

    sexos_disponibles = ['F', 'M']
    if tiene_sexo:
        df_a['_sexo'] = df_a[col_sexo_a].astype(str).str.strip().str.upper()
        df_b['_sexo'] = df_b[col_sexo_b].astype(str).str.strip().str.upper()
        df_a.loc[df_a['_sexo'].isin(['NAN', 'NONE', '', 'NULL']), '_sexo'] = np.nan
        df_b.loc[df_b['_sexo'].isin(['NAN', 'NONE', '', 'NULL']), '_sexo'] = np.nan

        sa = set(df_a['_sexo'].dropna().unique())
        sb = set(df_b['_sexo'].dropna().unique())
        unidos = sorted(list(sa.union(sb)))
        if unidos:
            sexos_disponibles = unidos

    edad_min = filtros.get('edad_min')
    edad_max = filtros.get('edad_max')
    sexo_sel = filtros.get('sexo', 'AMBOS')

    if tiene_edad:
        if edad_min is not None:
            df_a = df_a[df_a['_edad'] >= edad_min]
            df_b = df_b[df_b['_edad'] >= edad_min]
        if edad_max is not None:
            df_a = df_a[df_a['_edad'] <= edad_max]
            df_b = df_b[df_b['_edad'] <= edad_max]

    if tiene_sexo and sexo_sel and sexo_sel != 'AMBOS':
        df_a = df_a[df_a['_sexo'] == sexo_sel.upper()]
        df_b = df_b[df_b['_sexo'] == sexo_sel.upper()]

    insights = []
    res = {
        'nombre_a': nombre_a,
        'nombre_b': nombre_b,
        'metadatos_comunes': metadatos_comunes,
        'tiene_edad': tiene_edad,
        'tiene_sexo': tiene_sexo,
        'edad_min_global': edad_min_global,
        'edad_max_global': edad_max_global,
        'sexos_disponibles': sexos_disponibles,
        'filas_orig_a': int(len(df_a_orig)),
        'filas_orig_b': int(len(df_b_orig)),
        'filas_a': int(len(df_a)),
        'filas_b': int(len(df_b)),
        'cols_a': int(df_a_orig.shape[1]),
        'cols_b': int(df_b_orig.shape[1]),
        'nulos_a': int(df_a_orig.isna().sum().sum()),
        'nulos_b': int(df_b_orig.isna().sum().sum()),
        'insights': insights,
    }

    # Contraste Etario con dominio exacto [edad_min, edad_max] elegido por el usuario
    if tiene_edad:
        s_a = df_a['_edad'].dropna().astype(int)
        s_b = df_b['_edad'].dropna().astype(int)
        if len(s_a) > 1 and len(s_b) > 1:
            t_stat, p_val = stats.ttest_ind(s_a, s_b, equal_var=False)
            media_a, media_b = float(s_a.mean()), float(s_b.mean())
            diff = round(abs(media_a - media_b), 2)
            mayor = nombre_a if media_a > media_b else nombre_b

            res['edad'] = {
                'n_valido_a': int(len(s_a)),
                'n_valido_b': int(len(s_b)),
                'media_a': round(media_a, 2),
                'media_b': round(media_b, 2),
                'mediana_a': round(float(s_a.median()), 2),
                'mediana_b': round(float(s_b.median()), 2),
                'std_a': round(float(s_a.std()), 2),
                'std_b': round(float(s_b.std()), 2),
                't_stat': round(float(t_stat), 4),
                'p_valor': f"{p_val:.4e}",
                'diferencia_sig': bool(p_val < 0.05)
            }
            if p_val < 0.05:
                insights.append(f"En el segmento seleccionado, {mayor} registra una edad promedio {diff} años superior (p = {p_val:.2e}).")
            else:
                insights.append(f"En el segmento seleccionado, no hay diferencia significativa en la edad promedio entre ambos datasets (p = {p_val:.2f}).")

            # Dominio horizontal dinámico acotado exactamente al rango [e_inicio, e_fin]
            e_inicio = int(edad_min) if edad_min is not None else int(min(s_a.min(), s_b.min()))
            e_fin = int(edad_max) if edad_max is not None else int(max(s_a.max(), s_b.max()))
            if e_fin < e_inicio:
                e_inicio, e_fin = e_fin, e_inicio

            edades_dominio = list(range(e_inicio, e_fin + 1))
            labels_eje = [str(e) for e in edades_dominio]
            cnt_a = s_a.value_counts().reindex(edades_dominio, fill_value=0)
            cnt_b = s_b.value_counts().reindex(edades_dominio, fill_value=0)

            pct_a = (cnt_a / max(len(s_a), 1) * 100).round(2)
            pct_b = (cnt_b / max(len(s_b), 1) * 100).round(2)

            res['tramos_edad'] = {
                'labels': labels_eje,
                'cnt_a': [int(x) for x in cnt_a.tolist()],
                'cnt_b': [int(x) for x in cnt_b.tolist()],
                'pct_a': [float(x) for x in pct_a.tolist()],
                'pct_b': [float(x) for x in pct_b.tolist()],
            }

    # Contraste por Sexo (limpio de NaNs)
    if tiene_sexo:
        sa_valid = df_a['_sexo'].dropna()
        sb_valid = df_b['_sexo'].dropna()
        if len(sa_valid) > 0 or len(sb_valid) > 0:
            dist_a = (sa_valid.value_counts(normalize=True) * 100).round(2).to_dict()
            dist_b = (sb_valid.value_counts(normalize=True) * 100).round(2).to_dict()
            categorias = sorted(list(set(dist_a.keys()).union(set(dist_b.keys()))))
            res['sexo'] = {
                'categorias': categorias,
                'pct_a': [dist_a.get(c, 0) for c in categorias],
                'pct_b': [dist_b.get(c, 0) for c in categorias],
            }

            if sexo_sel == 'AMBOS' and len(categorias) >= 2:
                tabla_chi = pd.DataFrame({'A': sa_valid.value_counts(), 'B': sb_valid.value_counts()}).fillna(0)
                if (tabla_chi.sum(axis=1) > 0).sum() >= 2:
                    chi2, p_chi, _, _ = stats.chi2_contingency(tabla_chi)
                    res['chi2_sexo'] = {
                        'chi2': round(float(chi2), 4),
                        'p_valor': f"{p_chi:.4e}",
                    }
                    if p_chi < 0.05:
                        insights.append(f"Diferencia significativa en la composición por sexo entre administraciones (Chi² = {chi2:.2f}, p = {p_chi:.2e}).")
                    else:
                        insights.append(f"Equilibrio de género estadísticamente equivalente entre ambas administraciones (Chi² = {chi2:.2f}, p = {p_chi:.2f}).")

    return res