import math
import pandas as pd

def procesar_unidad3(df: pd.DataFrame, n_input: int = 10, r_input: int = 3):
    # Cálculos generales interactivos
    resultados_interactivos = {
        'n': n_input,
        'r': r_input,
        'perm_simple': math.factorial(n_input) if n_input <= 20 else "Excede límite visual",
        'var_simple': math.perm(n_input, r_input) if n_input >= r_input else 0,
        'var_rep': n_input ** r_input,
        'comb_simple': math.comb(n_input, r_input) if n_input >= r_input else 0,
        'comb_rep': math.comb(n_input + r_input - 1, r_input),
    }

    # Aplicación directa al dataset (ej. comités de funcionarios o combinaciones de categorías)
    n_total = len(df)
    n_ministerios = int(df['ministerio'].nunique()) if 'ministerio' in df.columns else 15
    n_escalafones = int(df['escalafon'].nunique()) if 'escalafon' in df.columns else 4

    aplicacion_dataset = {
        'total_registros': n_total,
        'comite_3_sin_orden': f"{math.comb(min(n_total, 500), 3):,}" if n_total >= 3 else 0,
        'terna_3_con_orden': f"{math.perm(min(n_total, 500), 3):,}" if n_total >= 3 else 0,
        'n_ministerios': n_ministerios,
        'comb_ministerios_3': math.comb(n_ministerios, 3) if n_ministerios >= 3 else 0,
        'var_ministerios_3': math.perm(n_ministerios, 3) if n_ministerios >= 3 else 0,
        'producto_cartesiano_cat': n_ministerios * n_escalafones,
    }

    return {
        'interactivo': resultados_interactivos,
        'dataset_comb': aplicacion_dataset,
    }