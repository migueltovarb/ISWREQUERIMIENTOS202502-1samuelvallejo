class Contacto:

    def __init__(self, nombre, numero_telefono, correo_electronico, cargo):

        self.__nombre = nombre
        self.__numero_telefono = numero_telefono
        self.__correo_electronico = correo_electronico
        self.__cargo = cargo

    def darNombre(self):
        return self.__nombre
    
    def darNumeroTelefono(self):
        return self.__numero_telefono
    
    def darCorreo_electronico(self):
        return self.__correo_electronico
    
    def darCargo(self):
        return self.__cargo
    
    def cambiarNombre(self, nombre):
        self.__nombre = nombre

    def cambiarNumero_telefono(self, numero_telefono):
        self.__numero_telefono = numero_telefono

    def cambiarCargo(self, cargo):
        self.__cargo = cargo

    def to_list(self):
        return [self.__nombre, self.__numero_telefono, self.__correo_electronico, self.__cargo]

import csv
import os
import time

ARCHIVO_CONTACTOS = "contactos.csv"

# =============================
# Funciones auxiliares
# =============================

def cargar_contactos():
    contactos = []
    if os.path.exists(ARCHIVO_CONTACTOS):
        with open(ARCHIVO_CONTACTOS, newline='', encoding='utf-8') as archivo:
            lector = csv.reader(archivo)
            for fila in lector:
                if fila:  # evitar filas vacías
                    contactos.append(Contacto(fila[0], fila[1], fila[2], fila[3]))
    return contactos

def guardar_contactos(contactos):
    with open(ARCHIVO_CONTACTOS, 'w', newline='', encoding='utf-8') as archivo:
        escritor = csv.writer(archivo)
        for c in contactos:
            escritor.writerow(c.to_list())

def buscar_contacto(contactos, criterio):
    criterio = criterio.lower()
    for c in contactos:
        if c.darNombre().lower() == criterio or c.darCorreoElectronico().lower() == criterio:
            return c
    return None

# =============================
# Funcionalidades del sistema
# =============================

def registrar_contacto(contactos):
    print("\n--- REGISTRAR NUEVO CONTACTO ---")
    nombre = input("Nombre: ")
    numero = input("Número de teléfono: ")
    correo = input("Correo electrónico: ")
    cargo = input("Cargo: ")

    # Validar correo duplicado
    if any(c.darCorreoElectronico().lower() == correo.lower() for c in contactos):
        print("Ya existe un contacto con ese correo electrónico.")
        return

    nuevo = Contacto(nombre, numero, correo, cargo)
    contactos.append(nuevo)
    guardar_contactos(contactos)
    print(" Contacto registrado exitosamente.")

def listar_contactos(contactos):
    print("\n--- LISTA DE CONTACTOS ---")
    if not contactos:
        print("No hay contactos registrados.")
    else:
        for i, c in enumerate(contactos, 1):
            print(f"{i}. {c.darNombre()} | {c.darNumeroTelefono()} | {c.darCorreoElectronico()} | {c.darCargo()}")

def buscar_y_mostrar_contacto(contactos):
    print("\n--- BUSCAR CONTACTO ---")
    criterio = input("Ingrese el nombre o correo: ")
    start = time.time()
    encontrado = buscar_contacto(contactos, criterio)
    end = time.time()

    if encontrado:
        print(f"\n Contacto encontrado (en {round(end - start, 4)} seg):")
        print(f"Nombre: {encontrado.darNombre()}")
        print(f"Teléfono: {encontrado.darNumeroTelefono()}")
        print(f"Correo: {encontrado.darCorreoElectronico()}")
        print(f"Cargo: {encontrado.darCargo()}")
    else:
        print(" No se encontró ningún contacto con ese nombre o correo.")

def eliminar_contacto(contactos):
    print("\n--- ELIMINAR CONTACTO ---")
    criterio = input("Ingrese el nombre o correo del contacto a eliminar: ")
    contacto = buscar_contacto(contactos, criterio)
    if contacto:
        contactos.remove(contacto)
        guardar_contactos(contactos)
        print("Contacto eliminado correctamente.")
    else:
        print("No se encontró el contacto a eliminar.")

# =============================
# Menú principal
# =============================

def menu():
    contactos = cargar_contactos()
    while True:
        print("\n===== DIRECTORIO CONNECTME =====")
        print("1. Registrar nuevo contacto")
        print("2. Buscar contacto por nombre o correo")
        print("3. Listar todos los contactos")
        print("4. Eliminar un contacto")
        print("5. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_contacto(contactos)
        elif opcion == "2":
            buscar_y_mostrar_contacto(contactos)
        elif opcion == "3":
            listar_contactos(contactos)
        elif opcion == "4":
            eliminar_contacto(contactos)
        elif opcion == "5":
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu()