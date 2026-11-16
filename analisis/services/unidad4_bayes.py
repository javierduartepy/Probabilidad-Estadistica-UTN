import pandas as pd
import numpy as np

def procesar_unidad4(df: pd.DataFrame, target_col: str = None):
    cols_cat = [c for c in df.select_dtypes(exclude=[np.number]).columns if 2 <= df[c].nunique() <= 10]
    if not target_col or target_col not in cols_cat:
        target_col = 'sexo' if 'sexo' in cols_cat else (cols_cat[0] if cols_cat else None)

    if not target_col:
        return {'error': 'No se encontraron variables categóricas con 2 a 10 clases.'}

    # Elegimos hasta 2 variables predictoras categóricas distintas al target
    predictoras = [c for c in cols_cat if c != target_col][:2]
    
    datos = df[[target_col] + predictoras].dropna().copy()
    clases = datos[target_col].unique().tolist()
    total = len(datos)

    # 1. Probabilidades a priori P(C)
    priors = {c: len(datos[datos[target_col] == c]) / total for c in clases}

    # 2. Verosimilitudes P(X_i | C) con suavizado de Laplace (+1)
    likelihoods = {}
    for col in predictoras:
        likelihoods[col] = {}
        valores_col = datos[col].unique()
        k_vals = len(valores_col)
        for c in clases:
            sub = datos[datos[target_col] == c]
            n_c = len(sub)
            likelihoods[col][c] = {
                val: (len(sub[sub[col] == val]) + 1) / (n_c + k_vals)
                for val in valores_col
            }

    # 3. Evaluación del clasificador sobre el dataset
    aciertos = 0
    matriz_confusion = {c_real: {c_pred: 0 for c_pred in clases} for c_real in clases}

    for _, fila in datos.iterrows():
        mejor_clase = None
        mejor_score = -1.0
        for c in clases:
            prob = priors[c]
            for col in predictoras:
                prob *= likelihoods[col][c].get(fila[col], 1e-6)
            if prob > mejor_score:
                mejor_score = prob
                mejor_clase = c
        
        real = fila[target_col]
        matriz_confusion[real][mejor_clase] += 1
        if real == mejor_clase:
            aciertos += 1

    accuracy = round((aciertos / total) * 100, 2) if total > 0 else 0

    return {
        'cols_cat': cols_cat,
        'target_col': target_col,
        'predictoras': predictoras,
        'priors': {str(k): round(v * 100, 2) for k, v in priors.items()},
        'accuracy': accuracy,
        'total_evaluados': total,
        'aciertos': aciertos,
        'errores': total - aciertos,
        'clases': [str(c) for c in clases],
        'matriz_confusion': matriz_confusion,
    }