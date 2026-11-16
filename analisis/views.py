import os
from .services.data_loader import DATASETS_DIR
from django.shortcuts import render, redirect
from django.contrib import messages
from .services.data_loader import guardar_dataset, obtener_df_filtrado, listar_datasets, DATASETS_DIR
from .services.unidad1_auditoria import procesar_unidad1
from .services.unidad2_descriptiva import procesar_unidad2
from .services.unidad3_combinatoria import procesar_unidad3
from .services.unidad4_bayes import procesar_unidad4
from .services.unidad5_discretas import procesar_unidad5
from .services.unidad6_tcl import procesar_unidad6
from .services.unidad7_inferencia import procesar_unidad7
from .services.comparador import comparar_datasets

def subir_dataset(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        nombre = guardar_dataset(request.FILES['archivo_csv'])
        request.session['dataset_activo'] = nombre
        messages.success(request, f'Dataset "{nombre}" cargado y seleccionado como activo.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

def seleccionar_dataset(request):
    if request.method == 'POST' and request.POST.get('dataset_nombre'):
        request.session['dataset_activo'] = request.POST.get('dataset_nombre')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

def _contexto_base(request):
    df, activo, disponibles, filtros = obtener_df_filtrado(request)
    return df, {
        'dataset_activo': activo,
        'datasets_disponibles': disponibles,
        'filtros': filtros,
        'tiene_datos': df is not None and len(df) > 0,
    }

def dashboard(request):
    df, ctx = _contexto_base(request)
    if df is not None:
        ctx['filas'], ctx['columnas'] = df.shape
        ctx['preview'] = df.head(10).to_html(classes='table table-sm table-striped table-hover', index=False)
    return render(request, 'analisis/dashboard.html', ctx)

def vista_unidad1(request):
    df, ctx = _contexto_base(request)
    if df is None or len(df) == 0: return redirect('dashboard')
    
    # Ruta absoluta del dataset activo actual
    ruta_activa = os.path.join(DATASETS_DIR, ctx['dataset_activo'])
    
    ctx['data'] = procesar_unidad1(df, ruta_activa)
    return render(request, 'analisis/unidad1.html', ctx)

def vista_unidad2(request):
    df, ctx = _contexto_base(request)
    if df is None or len(df) == 0: return redirect('dashboard')
    ctx['data'] = procesar_unidad2(df, request.GET.get('col_num'), request.GET.get('col_cat'))
    return render(request, 'analisis/unidad2.html', ctx)

def vista_unidad3(request):
    df, ctx = _contexto_base(request)
    if df is None or len(df) == 0: return redirect('dashboard')
    ctx['data'] = procesar_unidad3(df, int(request.GET.get('n', 10)), int(request.GET.get('r', 3)))
    return render(request, 'analisis/unidad3.html', ctx)

def vista_unidad4(request):
    df, ctx = _contexto_base(request)
    if df is None or len(df) == 0: return redirect('dashboard')
    ctx['data'] = procesar_unidad4(df, request.GET.get('target'))
    return render(request, 'analisis/unidad4.html', ctx)

def vista_unidad5(request):
    df, ctx = _contexto_base(request)
    if df is None or len(df) == 0: return redirect('dashboard')
    ctx['data'] = procesar_unidad5(df, int(request.GET.get('n_ensayos', 10)))
    return render(request, 'analisis/unidad5.html', ctx)

def vista_unidad6(request):
    df, ctx = _contexto_base(request)
    if df is None or len(df) == 0: return redirect('dashboard')
    ctx['data'] = procesar_unidad6(df, request.GET.get('col_num'))
    return render(request, 'analisis/unidad6.html', ctx)

def vista_unidad7(request):
    df, ctx = _contexto_base(request)
    if df is None or len(df) == 0: return redirect('dashboard')
    ctx['data'] = procesar_unidad7(df, request.GET.get('col_num'))
    return render(request, 'analisis/unidad7.html', ctx)

def vista_comparar(request):
    _, ctx = _contexto_base(request)
    disponibles = ctx['datasets_disponibles']
    ds_a = request.GET.get('ds_a', disponibles[0] if len(disponibles) > 0 else '')
    ds_b = request.GET.get('ds_b', disponibles[1] if len(disponibles) > 1 else ds_a)

    edad_min_raw = request.GET.get('edad_min', '')
    edad_max_raw = request.GET.get('edad_max', '')
    sexo_sel = request.GET.get('sexo', 'AMBOS')
    metrica_graf = request.GET.get('metrica_graf', 'tramos_edad')
    tipo_graf = request.GET.get('tipo_graf', 'bar')

    filtros_comp = {
        'edad_min': int(edad_min_raw) if edad_min_raw.isdigit() else None,
        'edad_max': int(edad_max_raw) if edad_max_raw.isdigit() else None,
        'sexo': sexo_sel,
    }

    comp = comparar_datasets(ds_a, ds_b, filtros_comp) if ds_a and ds_b else None

    ctx.update({
        'ds_a': ds_a,
        'ds_b': ds_b,
        'edad_min_sel': edad_min_raw if edad_min_raw else (comp['edad_min_global'] if comp else 18),
        'edad_max_sel': edad_max_raw if edad_max_raw else (comp['edad_max_global'] if comp else 90),
        'sexo_sel': sexo_sel,
        'metrica_graf': metrica_graf,
        'tipo_graf': tipo_graf,
        'comp': comp,
    })
    return render(request, 'analisis/comparar.html', ctx)

def vista_bienvenida(request):
    _, ctx = _contexto_base(request)
    return render(request, 'analisis/bienvenida.html', ctx)