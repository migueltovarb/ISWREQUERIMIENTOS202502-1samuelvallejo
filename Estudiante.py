class Estudiante:

    def __init__(self, nombre, edad, correo_electronico, ID, carnet):
        self.__nombre = nombre
        self.__edad = edad
        self.__correo_electronico = correo_electronico
        self.__ID = ID
        self.__carnet = carnet

    def darNombre(self):
        return self.__nombre
    
    def darEdad(self):
        return self.__edad
    
    def darCorreo_electronico(self):
        return self.__correo_electronico
    
    def darID(self):
        return self.__ID
    
    def darCarnet(self):
        return self.__carnet
    
    def cambiarNombre(self, nombre):
        self.__nombre = nombre

    def cambiarEdad(self, edad):
        self.__edad = edad

    def cambiarCorreo_electronico(self, correo_electronico):
        self.__correo_electronico = correo_electronico

    def cambiarID(self, ID):
        self.__ID = ID

    def cambiarCarnet(self, carnet):
        self.__carnet = carnet