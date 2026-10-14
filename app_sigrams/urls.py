from django.urls import path
from . import views
from .views import (
    ListaMarcasView,
    NuevaMarcaView,
    EditarMarcaView,
    DetalleMarcaView,
    cargar_campos,
    buscar_marca_por_nombre,
    get_marcas_por_productor,
    get_campos_por_productor,
    crear_campo_poligono,
    actualizar_campo_poligono,
    buscar_imagen_similar,
    verificar_imagen_ajax,
)

urlpatterns = [

    # =========================
    # AUTENTICACIÓN
    # =========================
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('activar-cuenta/', views.activar_cuenta_view, name='activar_cuenta'),
    path('cuentas-pendientes/', views.cuentas_pendientes, name='cuentas_pendientes'),
    path('cuentas-pendientes/<int:user_id>/aprobar/', views.aprobar_cuenta, name='aprobar_cuenta'),
    path('cuentas-pendientes/<int:user_id>/rechazar/', views.rechazar_cuenta, name='rechazar_cuenta'),

    # =========================
    # PRODUCTORES
    # =========================
    path('productores/', views.lista_productores, name='lista_productores'),
    path('productores/nuevo/', views.nuevo_productor, name='nuevo_productor'),
    path('productores/<int:pk>/', views.detalle_productor, name='detalle_productor'),
    path('productores/<int:pk>/editar/', views.editar_productor, name='editar_productor'),
    path('productores/<int:pk>/eliminar/', views.eliminar_productor, name='eliminar_productor'),

    # =========================
    # MARCAS Y SEÑALES
    # =========================
    path('marcas/', ListaMarcasView.as_view(), name='lista_marcas'),
    path('marcas/nueva/', NuevaMarcaView.as_view(), name='nueva_marca'),
    path('marcas/<int:pk>/editar/', EditarMarcaView.as_view(), name='editar_marca'),
    path('marcas/<int:pk>/', DetalleMarcaView.as_view(), name='detalle_marca'),

    # =========================
    # SOLICITUDES
    # =========================
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/nueva/', views.nueva_solicitud, name='nueva_solicitud'),
    path('solicitudes/<int:pk>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('solicitudes/<int:pk>/editar/', views.editar_solicitud, name='editar_solicitud'),
    path('solicitudes/<int:pk>/revision/', views.revision_solicitud, name='revision_solicitud'),
    path('solicitudes/<int:pk>/<str:accion>/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('dashboard-solicitudes/', views.dashboard_solicitudes, name='dashboard_solicitudes'),

    # =========================
    # AJAX (IMPORTANTE: agrupado)
    # =========================
    path('ajax/marcas/<int:productor_id>/', get_marcas_por_productor, name='ajax_marcas'),
    path('ajax/campos/<int:productor_id>/', get_campos_por_productor, name='ajax_campos'),
    path('ajax/campos/crear-poligono/', crear_campo_poligono, name='ajax_crear_campo_poligono'),
    path('ajax/campos/<int:campo_id>/actualizar-poligono/', actualizar_campo_poligono, name='ajax_actualizar_campo_poligono'),
    path('ajax/imagenes-marcas/', views.get_imagenes_marcas, name='ajax_imagenes_marcas'),
    path('ajax/buscar-imagen-similar/', buscar_imagen_similar, name='ajax_buscar_imagen_similar'),
    path('ajax/verificar-imagen/', verificar_imagen_ajax, name='ajax_verificar_imagen'),
    path('ajax/marca-detalle/<int:marca_id>/', views.detalle_marca_ajax, name='ajax_detalle_marca'),
    path('ajax/productor-tiene-marcas/<int:productor_id>/', views.verificar_marcas_productor_ajax, name='ajax_verificar_marcas_productor'),

    # =========================
    # BÚSQUEDA POR IMAGEN (página dedicada — escenario policial)
    # =========================
    path('marcas/buscar-por-imagen/', buscar_imagen_similar, name='buscar_imagen'),

    # =========================
    # OTRAS VISTAS
    # =========================
    path('cargar-campos/', cargar_campos, name='cargar_campos'),

    # =========================
    # API
    # =========================
    path('api/productores/geojson/', views.api_productores_geojson, name='api_productores_geojson'),

    # =========================
    # REPORTES
    # =========================
    path('reportes/ingresos/', views.reporte_ingresos, name='reporte_ingresos'),


    # URL temporal para verificar que las vistas funcionan
    path('test/marcas/', views.test_marcas_view, name='test_marcas'),


    path('documentos/<int:documento_id>/eliminar/', views.eliminar_documento, name='eliminar_documento'),

    # Rutas para reportes PDF y Excel
    path('reportes/productores/pdf/', views.reporte_productores_pdf, name='reporte_productores_pdf'),
    path('reportes/marcas/pdf/', views.reporte_marcas_pdf, name='reporte_marcas_pdf'),
    path('reportes/solicitudes/pdf/', views.reporte_solicitudes_pdf, name='reporte_solicitudes_pdf'),
    path('reportes/productores/excel/', views.reporte_productores_excel, name='reporte_productores_excel'),
    path('reportes/marcas/excel/', views.reporte_marcas_excel, name='reporte_marcas_excel'),
    path('reportes/solicitudes/excel/', views.reporte_solicitudes_excel, name='reporte_solicitudes_excel'),

    # Ruta para el dashboard del administrador
    path('admin-dashboard/', views.dashboard_admin, name='dashboard_admin'),
    
    # Rutas para reportes de usuarios (solo para admin)
    path('reporte/usuarios/pdf/', views.reporte_usuarios_pdf, name='reporte_usuarios_pdf'),
    path('reporte/usuarios/excel/', views.reporte_usuarios_excel, name='reporte_usuarios_excel'),

    # Rutas para el historial de eliminaciones (solo para admin)
    path('historial-eliminaciones/', views.historial_eliminaciones, name='historial_eliminaciones'),    

    # Ruta para buscar marcas por nombre (usada en AJAX)
    path('ajax/buscar-marca-nombre/', buscar_marca_por_nombre, name='ajax_buscar_marca_nombre'),

    # Rutas para el rol Inspector
    path('inspector/', views.busqueda_inspector, name='busqueda_inspector'),
    path('inspector/marca/<int:marca_id>/', views.detalle_inspector, name='detalle_inspector'),

    # Ruta para generar carnet PDF
    path('marcas/<int:marca_id>/carnet/', views.generar_carnet_pdf, name='generar_carnet'),

]
