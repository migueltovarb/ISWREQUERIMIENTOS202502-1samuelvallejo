from django.contrib import admin
from .models import (
    Categoria, Producto, TamanoProducto, Extra,
    Estudiante, Promocion, Pedido, ItemPedido,
    Carrito, ItemCarrito
)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden']
    list_editable = ['orden']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio_base', 'disponibilidad']
    list_filter = ['categoria', 'disponibilidad']
    search_fields = ['nombre', 'descripcion']

@admin.register(TamanoProducto)
class TamanoProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'nombre', 'precio_adicional']

@admin.register(Extra)
class ExtraAdmin(admin.ModelAdmin):
    list_display = ['producto', 'nombre', 'precio', 'es_obligatorio']
    list_filter = ['es_obligatorio']

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ['user', 'correo_institucional', 'es_verificado', 'numero_compras']
    list_filter = ['es_verificado']

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'porcentaje_descuento', 'tipo', 'activa', 'prioridad']
    list_filter = ['activa', 'tipo']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['numero_pedido', 'usuario', 'estado', 'total', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['numero_pedido', 'usuario__username']
    readonly_fields = ['numero_pedido', 'subtotal', 'impuestos', 'descuentos', 'total']

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'producto', 'cantidad', 'subtotal']

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_actualizacion']

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['carrito', 'producto', 'cantidad']
