from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal
from decimal import Decimal
from datetime import timedelta

from .models import (
    Categoria,
    Producto,
    TamanoProducto,
    Extra,
    Carrito,
    ItemCarrito,
    Promocion,
    Pedido,
    ItemPedido,
    Estudiante,
)
import json

def _ensure_estudiante(user):
    """Crea el perfil de estudiante si no existe y lo marca verificado para promos."""
    if hasattr(user, 'estudiante'):
        return user.estudiante
    correo = user.email or f"{user.username}@campus.local"
    estudiante, _ = Estudiante.objects.get_or_create(
        user=user,
        defaults={
            'correo_institucional': correo,
            'es_verificado': True,
        },
    )
    return estudiante


def _promocion_estudiante(user):
    """Devuelve la primera promoción activa aplicable para el estudiante."""
    estudiante = _ensure_estudiante(user)
    if not estudiante.es_verificado:
        return None

    if not Promocion.objects.filter(activa=True, tipo='estudiante').exists():
        Promocion.objects.get_or_create(
            nombre='Promo estudiantes frecuentes',
            defaults={
                'descripcion': '10% para estudiantes frecuentes',
                'porcentaje_descuento': Decimal('10.00'),
                'tipo': 'estudiante',
                'activa': True,
                'compras_requeridas': 3,
                'dias_periodo': 30,
                'prioridad': 1,
            },
        )

    promociones = Promocion.objects.filter(activa=True, tipo='estudiante').order_by('-prioridad')
    for promo in promociones:
        if estudiante.es_elegible_promocion(promo.dias_periodo, promo.compras_requeridas):
            return promo
    return None

"""
Módulo de vistas de la cafetería.

Historias de usuario implementadas:

HU_024 – Hacer pedidos desde el celular
    - Ver menú con categorías y productos     -> menu_principal
    - Ver detalle de un producto              -> detalle_producto
    - Agregar productos al carrito            -> agregar_al_carrito
    - Ver y editar el carrito                 -> ver_carrito
    - Actualizar cantidades del carrito       -> actualizar_cantidad_carrito
    - Eliminar productos del carrito          -> eliminar_item_carrito

HU_025 – Pago en línea
    - Ver resumen antes de pagar              -> resumen_pago
    - Procesar el pago en línea               -> procesar_pago
    - Mostrar confirmación de pedido          -> confirmacion_pedido

HU_026 – Recoger en ventanilla
    - Lista de pedidos a entregar             -> ventanilla
    - Confirmar entrega al estudiante         -> entregar_pedido

HU_027 – Promociones para estudiantes frecuentes
    - Detectar si el usuario es estudiante    -> uso de request.user.estudiante
    - Calcular y mostrar promociones          -> menu_principal, ver_carrito,
                                                 resumen_pago, procesar_pago
"""


@login_required
def menu_principal(request):
    """HU_024: Mostrar menú con categorías y productos"""
    categorias = Categoria.objects.all()
    categoria_seleccionada = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda', '')
    
    if categoria_seleccionada:
        productos = Producto.objects.filter(categoria_id=categoria_seleccionada)
    else:
        productos = Producto.objects.all()
    
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda) |
            Q(categoria__nombre__icontains=busqueda)
        )
    
    estudiante = _ensure_estudiante(request.user)
    es_estudiante = estudiante.es_verificado
    promocion_aplicable = _promocion_estudiante(request.user) if es_estudiante else None
    
    # Obtener o crear carrito
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items_carrito = carrito.items.all()
    total_carrito = sum(item.get_precio_total() for item in items_carrito)
    carrito_count = items_carrito.count()
    
    context = {
        'categorias': categorias,
        'productos': productos,
        'categoria_seleccionada': categoria_seleccionada,
        'busqueda': busqueda,
        'carrito': carrito,
        'items_carrito': items_carrito,
        'total_carrito': total_carrito,
        'carrito_count': carrito_count,
        'promocion_aplicable': promocion_aplicable,
        'es_estudiante': es_estudiante,
    }
    
    return render(request, 'menu.html', context)


@login_required
def detalle_producto(request, producto_id):
    """HU_024: Mostrar detalle de producto con extras y tamaños"""
    producto = get_object_or_404(Producto, id=producto_id)
    tamanos = producto.tamanos.all()
    extras = producto.extras.all()
    
    context = {
        'producto': producto,
        'tamanos': tamanos,
        'extras': extras,
    }
    
    return render(request, 'detalle_producto.html', context)


@login_required
@require_POST
def agregar_al_carrito(request):
    """HU_024: Agregar producto al carrito (AJAX o formulario normal)"""
    producto_id = request.POST.get('producto_id')
    cantidad = int(request.POST.get('cantidad', 1))
    tamano_id = request.POST.get('tamano_id')
    extras_ids = request.POST.getlist('extras[]')
    personalizacion = request.POST.get('personalizacion', '')
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Validar stock
    if producto.disponibilidad != 'disponible':
        if is_ajax:
            return JsonResponse({'error': 'Producto no disponible'}, status=400)
        messages.error(request, 'Este producto no está disponible')
        return redirect('cafeteria:menu_principal')
    
    # Validar extras obligatorios
    extras_obligatorios = producto.extras.filter(es_obligatorio=True)
    if extras_obligatorios.exists():
        obligatorios_faltantes = extras_obligatorios.exclude(id__in=extras_ids)
        if obligatorios_faltantes.exists():
            if is_ajax:
                return JsonResponse(
                    {'error': 'Debes seleccionar todas las opciones obligatorias'},
                    status=400
                )
            messages.error(
                request,
                'Debes seleccionar las opciones obligatorias para este producto'
            )
            return redirect('cafeteria:detalle_producto', producto_id=producto.id)
    
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    
    # Crear item del carrito
    item = ItemCarrito.objects.create(
        carrito=carrito,
        producto=producto,
        cantidad=cantidad,
        personalizacion=personalizacion
    )
    
    if tamano_id:
        item.tamano = TamanoProducto.objects.get(id=tamano_id)
        item.save()
    
    if extras_ids:
        item.extras_seleccionados.set(extras_ids)
    
    data = {
        'success': True,
        'mensaje': 'Producto agregado al carrito',
        'total_items': carrito.items.count()
    }
    
    if is_ajax:
        return JsonResponse(data)
    
    messages.success(request, 'Producto agregado al carrito')
    return redirect('cafeteria:ver_carrito')


@login_required
def ver_carrito(request):
    """HU_024: Ver carrito con totales y promociones"""
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    
    subtotal = sum(item.get_precio_total() for item in items) or Decimal('0')
    impuestos = subtotal * Decimal('0.10')
    
    descuento = Decimal('0')
    promocion_aplicada = _promocion_estudiante(request.user)
    if promocion_aplicada:
        descuento = (subtotal * promocion_aplicada.porcentaje_descuento) / Decimal('100')
    
    total = subtotal + impuestos - descuento
    
    # HU_028: Calcular tiempo estimado de entrega
    num_items = items.count()
    tiempo_estimado = 15 + (num_items * 5)  # 15 min base + 5 min por item
    
    context = {
        'carrito': carrito,
        'items': items,
        'subtotal': subtotal,
        'impuestos': impuestos,
        'descuento': descuento,
        'total': total,
        'promocion_aplicada': promocion_aplicada,
        'tiempo_estimado': tiempo_estimado,
    }
    
    return render(request, 'carrito.html', context)


@login_required
@require_POST
def actualizar_cantidad_carrito(request):
    """HU_024: Actualizar cantidad en carrito"""
    item_id = request.POST.get('item_id')
    accion = request.POST.get('accion')  # 'incrementar' o 'decrementar'
    
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    
    if accion == 'incrementar':
        item.cantidad += 1
    elif accion == 'decrementar':
        item.cantidad -= 1
        if item.cantidad <= 0:
            item.delete()
            return JsonResponse({'success': True, 'eliminado': True})
    
    item.save()
    
    return JsonResponse({
        'success': True,
        'nueva_cantidad': item.cantidad,
        'subtotal': float(item.get_precio_total())
    })


@login_required
@require_POST
def eliminar_item_carrito(request):
    """HU_024: Eliminar item del carrito (usado vía AJAX)"""
    item_id = request.POST.get('item_id')
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    
    return JsonResponse({'success': True})


@login_required
def resumen_pago(request):
    """HU_024 y HU_025: Resumen antes de pagar"""
    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.all()
    
    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('cafeteria:menu_principal')
    
    subtotal = sum(item.get_precio_total() for item in items) or Decimal('0')
    impuestos = subtotal * Decimal('0.10')
    
    descuento = Decimal('0')
    promocion_aplicada = _promocion_estudiante(request.user)
    if promocion_aplicada:
        descuento = (subtotal * promocion_aplicada.porcentaje_descuento) / Decimal('100')
    
    total = subtotal + impuestos - descuento
    
    context = {
        'items': items,
        'subtotal': subtotal,
        'impuestos': impuestos,
        'descuento': descuento,
        'total': total,
        'promocion_aplicada': promocion_aplicada,
    }
    
    return render(request, 'resumen_pago.html', context)


@login_required
def procesar_pago(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metodo no permitido'}, status=405)

    carrito = Carrito.objects.filter(usuario=request.user).first()
    items = carrito.items.select_related('producto', 'tamano').prefetch_related('extras_seleccionados') if carrito else []

    if not carrito or not items or not items.exists():
        return JsonResponse({'success': False, 'error': 'El carrito esta vacio'}, status=400)

    subtotal = sum((item.get_precio_total() for item in items), Decimal('0'))
    impuestos = subtotal * Decimal('0.10')

    descuento = Decimal('0')
    promocion_aplicada = _promocion_estudiante(request.user)
    if promocion_aplicada:
        descuento = (subtotal * promocion_aplicada.porcentaje_descuento) / Decimal('100')

    total = subtotal + impuestos - descuento

    numero_pedido = None
    while not numero_pedido:
        posible = Pedido().generar_numero_pedido()
        if not Pedido.objects.filter(numero_pedido=posible).exists():
            numero_pedido = posible

    pedido = Pedido.objects.create(
        usuario=request.user,
        numero_pedido=numero_pedido,
        subtotal=subtotal,
        impuestos=impuestos,
        descuentos=descuento,
        total=total,
        estado='pendiente',
        metodo_pago=request.POST.get('metodo_pago', 'tarjeta'),
        franja_entrega=request.POST.get('franja_entrega', 'ahora'),
        promocion_aplicada=promocion_aplicada,
    )

    # Actualizar compras del estudiante
    estudiante = _ensure_estudiante(request.user)
    estudiante.numero_compras = (estudiante.numero_compras or 0) + 1
    estudiante.ultima_compra = timezone.now()
    estudiante.save()

    # Calcular tiempo estimado de entrega
    num_items = items.count()
    tiempo_estimado = 15 + (num_items * 5)
    pedido.tiempo_estimado = tiempo_estimado
    pedido.hora_estimada_entrega = (timezone.now() + timedelta(minutes=tiempo_estimado)).time()
    pedido.save(update_fields=['tiempo_estimado', 'hora_estimada_entrega'])

    for item in items:
        precio_unitario = item.producto.precio_base
        if item.tamano:
            precio_unitario += item.tamano.precio_adicional
        for extra in item.extras_seleccionados.all():
            precio_unitario += extra.precio

        pedido_item = ItemPedido.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            tamano=item.tamano,
            personalizacion=item.personalizacion,
            precio_unitario=precio_unitario,
            subtotal=precio_unitario * item.cantidad,
        )
        pedido_item.extras_seleccionados.set(item.extras_seleccionados.all())

    items.delete()

    redirect_url = reverse('cafeteria:confirmacion_pedido', args=[pedido.id])

    return JsonResponse({
        'success': True,
        'redirect_url': redirect_url,
    })


@login_required
def confirmacion_pedido(request, pedido_id):
    """Confirmación de pedido exitoso"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    context = {
        'pedido': pedido,
    }
    
    return render(request, 'confirmacion_pedido.html', context)


@login_required
def ventanilla(request):
    """HU_026: Vista de ventanilla para recoger pedidos"""
    # Búsqueda
    busqueda = request.GET.get('busqueda', '')
    pedidos = Pedido.objects.filter(estado__in=['pagado', 'listo', 'en_preparacion'])
    
    if busqueda:
        pedidos = pedidos.filter(
            Q(numero_pedido__icontains=busqueda) |
            Q(usuario__username__icontains=busqueda) |
            Q(usuario__first_name__icontains=busqueda)
        )
    
    # Detalle del pedido seleccionado
    pedido_id = request.GET.get('pedido')
    pedido_detalle = None
    if pedido_id:
        pedido_detalle = get_object_or_404(Pedido, id=pedido_id)
    
    context = {
        'pedidos': pedidos,
        'pedido_detalle': pedido_detalle,
        'busqueda': busqueda,
    }
    
    return render(request, 'ventanilla.html', context)


@login_required
@require_POST
def entregar_pedido(request, pedido_id):
    """HU_026: Entregar pedido al cliente (AJAX)"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Validar que esté pagado y listo
    if pedido.estado != 'listo':
        return JsonResponse({'error': 'El pedido no está listo para entregar'}, status=400)
    
    # Confirmar identidad del cliente (simulado)
    confirmacion = request.POST.get('confirmacion')
    if confirmacion != 'confirmar':
        return JsonResponse({'error': 'Debe confirmar la entrega'}, status=400)
    
    pedido.estado = 'entregado'
    pedido.save()
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Pedido entregado exitosamente'
    })


@login_required
def mis_pedidos(request):
    """Ver historial de pedidos del usuario"""
    pedidos = Pedido.objects.filter(usuario=request.user)
    
    context = {
        'pedidos': pedidos,
    }
    
    return render(request, 'mis_pedidos.html', context)
# Create your views here.
