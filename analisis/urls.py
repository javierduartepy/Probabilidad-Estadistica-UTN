from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_bienvenida, name='bienvenida'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('unidad-1/', views.vista_unidad1, name='unidad1'),
    path('unidad-2/', views.vista_unidad2, name='unidad2'),
    path('unidad-3/', views.vista_unidad3, name='unidad3'),
    path('unidad-4/', views.vista_unidad4, name='unidad4'),
    path('unidad-5/', views.vista_unidad5, name='unidad5'),
    path('unidad-6/', views.vista_unidad6, name='unidad6'),
    path('unidad-7/', views.vista_unidad7, name='unidad7'),
    path('comparar/', views.vista_comparar, name='comparar'),
    path('seleccionar-dataset/', views.seleccionar_dataset, name='seleccionar_dataset'),
    path('subir-dataset/', views.subir_dataset, name='subir_dataset'),
]