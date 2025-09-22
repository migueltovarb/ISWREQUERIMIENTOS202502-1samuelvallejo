from Estudiante import Estudiante
from Producto import Producto
from Pedido import Pedido

arroz_con_huevo = Producto(10000, "arroz_con_huevo", "desayuno")
cafe = Producto (3000, "cafe", "bebida")
croissant = Producto(4000, "croissant", "pan")
chocolate = Producto(6000, "chocolate", "bebida")
galletas = Producto(3000, "galletas", "comida")

Producto_lista = [arroz_con_huevo, cafe, croissant, chocolate, galletas]

print("bienvenidos a la cafeteria de la universidad")

nombre = input("\nIngrese su nombre: ")
edad = int(input("Ingrese su edad: "))
correo = input("Ingrese su correo electrónico: ")
id_est = input("Ingrese su ID: ")
carnet_valido = input("¿Tiene carnet válido? (s/n): ").strip().lower() == "s"

estudiante = Estudiante(nombre, edad, correo, id_est, carnet_valido)
pedido = Pedido(estudiante, [])

detener = True
while detener:
    print("Estos son los productos que hay en la cafeteria")
    i = 0
    for producto in Producto_lista:
        i += 1      
        print(f"{i}-producto: {producto.darNombre()} precio:{producto.darPrecio()}") 

   

    while True:
        eleccion = input("\nEscriba el número del producto para agregarlo (o 'fin' para terminar): ").strip()
        if eleccion.lower() == "fin":
            break
        if eleccion.isdigit() and 1 <= int(eleccion) <= len(Producto_lista):
            pedido.añadirProducto(Producto_lista[int(eleccion) - 1])
            print("Producto agregado.")
        else:
            print("Opción inválida, intente de nuevo.")

    total = sum(p.darPrecio() for p in pedido.darProducto())

    if estudiante.darCarnet():
        total_con_descuento = total * 0.9
        descuento_msg = "Se aplicó un 10% de descuento por carnet válido."
    else:
        total_con_descuento = total
        descuento_msg = "No se aplicó descuento."

    print("\n------ RESUMEN DEL PEDIDO ------")
    print(f"Estudiante: {estudiante.darNombre()}")
    for p in pedido.darProducto():
        print(f"- {p.darNombre()}  ${p.darPrecio()}")
    print(f"Total sin descuento: ${total}")
    print(descuento_msg)
    print(f"Total a pagar: ${total_con_descuento}")

    from datetime import datetime
    fecha = datetime.now().strftime("%Y-%m-%d")
    with open(f"ventas_{fecha}.txt", "a", encoding="utf-8") as f:
        f.write(f"\n{datetime.now()} - {estudiante.darNombre()} - Total: ${total_con_descuento}\n")
        for p in pedido.darProducto():
            f.write(f"   {p.darNombre()}  ${p.darPrecio()}\n")

    print("\nRegistro diario de ventas guardado correctamente.")
    detener = False
