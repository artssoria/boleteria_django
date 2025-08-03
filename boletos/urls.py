from django.urls import path
from . import views

urlpatterns =[
    path('nuevo/', views.crear_boleto, name='crear_boleto' ), 
    path('lista/', views.listar_boletos, name='listar_boletos'), 
   path('<int:pk>/', views.detalle_boleto, name='detalle_boleto'),
path('<int:pk>/editar/', views.editar_boleto, name='editar_boleto'),
path('<int:pk>/eliminar/', views.eliminar_boleto, name='eliminar_boleto'),
path('buscar/', views.buscar_boletos, name='buscar_boletos'),
path('filtro-fecha/', views.filtrar_por_fecha, name='filtrar_por_fecha'),
path('registro/', views.registro_usuario, name='registro'),
path('<int:pk>/comprobante/', views.generar_pdf_boleto, name='generar_pdf'),
]