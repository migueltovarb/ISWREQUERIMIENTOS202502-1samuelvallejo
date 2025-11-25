# proyecto_cafeteria/urls.py
from django.urls import path
from . import views

app_name = "cafeteria"

urlpatterns = [
    # Página principal del menú (la que muestra las tarjetas de productos)
    # Si tu vista se llama distinto, cambia menu_principal por el nombre real.
    path('', views.menu_principal, name='menu_principal'),

    # ---------------- HU_024 – Listado / detalle de productos ----------------
    path('producto/<int:producto_id>/', views.detalle_producto,
         name='detalle_producto'),

    # ---------------- Carrito ----------------
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/', views.agregar_al_carrito,
         name='agregar_al_carrito'),
    path('carrito/actualizar/', views.actualizar_cantidad_carrito,
         name='actualizar_cantidad_carrito'),
    path('carrito/eliminar/', views.eliminar_item_carrito,
         name='eliminar_item_carrito'),

    # ---------------- HU_025 – Pago en línea ----------------
    path('resumen-pago/', views.resumen_pago, name='resumen_pago'),
    path('procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('pedido/<int:pedido_id>/confirmacion/',
         views.confirmacion_pedido, name='confirmacion_pedido'),

    # ---------------- HU_026 – Recoger en ventanilla ----------------
    path('ventanilla/', views.ventanilla, name='ventanilla'),
    path('pedido/<int:pedido_id>/entregar/',
         views.entregar_pedido, name='entregar_pedido'),

    # ---------------- Historial de pedidos ----------------
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
]
