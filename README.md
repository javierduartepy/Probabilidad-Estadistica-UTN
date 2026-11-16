tpi_estadistica_django/
├── manage.py
├── requirements.txt
├── core/
│   ├── settings.py
│   └── urls.py
└── analisis/
    ├── services/                  <-- Lógica pura de Python/Pandas por unidad
    │   ├── __init__.py
    │   ├── data_loader.py         <-- Carga única y cache/sesión del CSV
    │   ├── unidad1_auditoria.py   <-- TP 1: Estructuras nativas, nulos, duplicados, rangos
    │   ├── unidad2_descriptiva.py <-- TP 2: Posición, dispersión, asimetría, outliers, datos p/ gráficos
    │   ├── unidad3_combinatoria.py<-- TP 3: Permutaciones, variaciones y combinaciones sobre el dataset
    │   ├── unidad4_bayes.py       <-- TP 4: Probabilidad condicional y Clasificador Naive Bayes propio
    │   ├── unidad5_discretas.py   <-- TP 5: Bernoulli, Binomial, Poisson + 10.000 simulaciones
    │   ├── unidad6_tcl.py         <-- TP 6: Ajuste continuo + Simulación TCL (n=5, 30, 100)
    │   └── unidad7_inferencia.py  <-- TP 7: IC Clásico vs Bootstrap, Chi-cuadrado, Regresión Lineal
    ├── templates/
    │   └── analisis/
    │       ├── base.html          <-- Navbar Bootstrap 5 + Formulario global de carga CSV
    │       ├── dashboard.html     <-- Resumen general + Diccionario de variables
    │       ├── unidad1.html
    │       ├── unidad2.html
    │       ├── unidad3.html
    │       ├── unidad4.html
    │       ├── unidad5.html
    │       ├── unidad6.html
    │       └── unidad7.html
    ├── urls.py
    └── views.py