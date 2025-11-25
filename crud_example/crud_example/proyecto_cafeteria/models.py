from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='categorias/')
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    DISPONIBILIDAD_CHOICES = [
        ('disponible', 'Disponible'),
        ('agotado', 'Agotado'),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    imagen = models.ImageField(upload_to='productos/')
    disponibilidad = models.CharField(max_length=20, choices=DISPONIBILIDAD_CHOICES, default='disponible')
    alergenos = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class TamanoProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='tamanos')
    nombre = models.CharField(max_length=50)  # Pequeno, Mediano, Grande
    precio_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.producto.nombre} - {self.nombre}"


class Extra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='extras')
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    es_obligatorio = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} (+${self.precio})"


class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    correo_institucional = models.EmailField(unique=True)
    es_verificado = models.BooleanField(default=False)
    ultima_compra = models.DateTimeField(null=True, blank=True)
    numero_compras = models.IntegerField(default=0)

    def es_elegible_promocion(self, dias=30, compras_minimas=3):
        if not self.es_verificado:
            return False
        if self.ultima_compra:
            fecha_limite = timezone.now() - timedelta(days=dias)
            if self.ultima_compra >= fecha_limite and self.numero_compras >= compras_minimas:
                return True
        return False

    def __str__(self):
        return self.user.username


class Promocion(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2)
    tipo = models.CharField(max_length=50, default='estudiante')  # estudiante, general, etc
    activa = models.BooleanField(default=True)
    compras_requeridas = models.IntegerField(default=3)
    dias_periodo = models.IntegerField(default=30)
    prioridad = models.IntegerField(default=0)

    class Meta:
        ordering = ['-prioridad']

    def __str__(self):
        return f"{self.nombre} - {self.porcentaje_descuento}%"


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En Preparacion'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('pagado', 'Pagado'),
    ]

    FRANJA_CHOICES = [
        ('ahora', 'Lo antes posible'),
        ('15min', '15 minutos'),
        ('30min', '30 minutos'),
        ('1hora', '1 hora'),
        ('personalizada', 'Personalizada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    numero_pedido = models.CharField(max_length=20, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    franja_entrega = models.CharField(max_length=20, choices=FRANJA_CHOICES, default='ahora')
    tiempo_estimado = models.IntegerField(help_text='Tiempo en minutos', null=True, blank=True)
    hora_estimada_entrega = models.TimeField(null=True, blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    promocion_aplicada = models.ForeignKey(Promocion, on_delete=models.SET_NULL, null=True, blank=True)

    metodo_pago = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    auth_code = models.CharField(max_length=100, blank=True)
    referencia = models.CharField(max_length=100, blank=True)

    observaciones = models.TextField(blank=True)

    def generar_numero_pedido(self):
        import random
        import string
        return f"PED-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

    def calcular_totales(self):
        subtotal = sum((item.subtotal for item in self.items.all()), Decimal('0'))
        impuestos = subtotal * Decimal('0.10')
        descuentos = self.descuentos if self.descuentos is not None else Decimal('0')
        if self.promocion_aplicada:
            descuentos = (subtotal * self.promocion_aplicada.porcentaje_descuento) / Decimal('100')

        self.subtotal = subtotal
        self.impuestos = impuestos
        self.descuentos = descuentos
        self.total = subtotal + impuestos - descuentos
        self.save()

    def calcular_tiempo_estimado(self):
        num_items = self.items.count()
        tiempo_base = 15
        tiempo_por_item = 5

        self.tiempo_estimado = tiempo_base + (num_items * tiempo_por_item)

        if self.franja_entrega == '15min':
            self.tiempo_estimado = max(self.tiempo_estimado, 15)
        elif self.franja_entrega == '30min':
            self.tiempo_estimado = max(self.tiempo_estimado, 30)
        elif self.franja_entrega == '1hora':
            self.tiempo_estimado = max(self.tiempo_estimado, 60)

        from datetime import datetime, timedelta
        hora_estimada = datetime.now() + timedelta(minutes=self.tiempo_estimado)
        self.hora_estimada_entrega = hora_estimada.time()
        self.save()

    def __str__(self):
        return f"{self.numero_pedido} - {self.usuario.username}"

    class Meta:
        ordering = ['-fecha_creacion']


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    tamano = models.ForeignKey(TamanoProducto, on_delete=models.SET_NULL, null=True, blank=True)
    extras_seleccionados = models.ManyToManyField(Extra, blank=True)
    personalizacion = models.TextField(blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def calcular_precio(self):
        precio = self.producto.precio_base

        if self.tamano:
            precio += self.tamano.precio_adicional

        for extra in self.extras_seleccionados.all():
            precio += extra.precio

        self.precio_unitario = precio
        self.subtotal = precio * self.cantidad
        self.save()

    def get_precio_total(self):
        return self.subtotal

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"


class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    tamano = models.ForeignKey(TamanoProducto, on_delete=models.SET_NULL, null=True, blank=True)
    extras_seleccionados = models.ManyToManyField(Extra, blank=True)
    personalizacion = models.TextField(blank=True)

    def get_precio_total(self):
        precio = self.producto.precio_base

        if self.tamano:
            precio += self.tamano.precio_adicional

        for extra in self.extras_seleccionados.all():
            precio += extra.precio

        return precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
