class Producto:

    def __init__(self, precio, nombre, tipo):
        self.__precio = precio
        self.__nombre = nombre
        self.__tipo = tipo

    def darPrecio(self):
        return self.__precio
    
    def darNombre(self):
        return self.__nombre
    
    def darTipo(self):
        return self.__tipo
    
    def cambiarPrecio(self, precio):
        self.__precio = precio

    def cambiarNombre(self, nombre):
        self.__nombre = nombre

    def cambiarTipo(self, tipo):
        self.__tipo = tipo