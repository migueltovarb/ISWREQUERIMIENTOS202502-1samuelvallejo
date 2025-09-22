class Pedido:

    def __init__(self, estudiante, productos):
        self.__estudiante = estudiante
        self.__productos = productos

    def darEstudiante(self):
        return self.__estudiante
    
    def darProducto(self):
        return self.__productos
    
    def cambiarEstudiante(self, estudiante):
        self.__estudiante = estudiante

    def añadirProducto(self, producto):
        self.__productos.append(producto)

    def eliminarProducto(self, producto):
        try:
            self.__productos.remove(producto)
        except ValueError:
            pass

    def verificarCarnet(self, carnet):
        try:
            return bool(carnet.darCarnet())
        except Exception:
            return False
