import datetime
import random
import functools
from abc import ABCMeta, abstractmethod

'''datetime → para manejar fechas de canciones
random → para generar datos aleatorios del catálogo
functools → para usar reduce
ABCMeta, abstractmethod → para crear clases abstractas'''



# EXCEPCIÓN
class TipoNoValido(Exception):
    def __init__(self, mensaje="Error: el tipo proporcionado no es válido"):
        self.message = mensaje
        super().__init__(self.message)

# GENERACIÓN DE ATRIBUTOS ALEATORIOS(como pide el enunciado)
def generar_atributos_aleatorios():
    return {
        "ritmo": round(random.uniform(0, 1), 2),
        "tono": round(random.uniform(0, 1), 2),
        "escala": round(random.uniform(0, 1), 2)
    }, {
        "felicidad": round(random.uniform(0, 1), 2),
        "bailabilidad": round(random.uniform(0, 1), 2),
        "energia": round(random.uniform(0, 1), 2)
    }

# MODELO
class Cancion:
    def __init__(self, id_cancion, titulo, fecha_creacion, atributos_sonoros, atributos_sentimentales):
        self.id_cancion = id_cancion
        self.titulo = titulo
        self.fecha_creacion = fecha_creacion
        self.atributos_sonoros = atributos_sonoros
        self.atributos_sentimentales = atributos_sentimentales

class Artista:
    def __init__(self, nombre, fecha_nacimiento, canciones):
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        self.canciones = canciones

class Playlist:
    def __init__(self, titulo, fecha_creacion, canciones):
        self.titulo = titulo
        self.fecha_creacion = fecha_creacion
        self.canciones = canciones

class Catalogo:
    def __init__(self, canciones, artistas, playlists):
        self.canciones = canciones
        self.artistas = artistas
        self.playlists = playlists
    def buscar_cancion_por_id(self, id_cancion):
        for cancion in self.canciones:
            if cancion.id_cancion == id_cancion:
                return cancion
        raise TipoNoValido("No existe una canción con ese id")
    
    # GENERACIÓN SIMPLE DE CATÁLOGO (Crea n canciones con atributos aleatorios.)
def generar_catalogo(n):
    canciones=[]
    for i in range(n):
        sonoros,sentimentales=generar_atributos_aleatorios()
        canciones.append(Cancion(i,f"Cancion_{i}",datetime.datetime.now(),sonoros,sentimentales))
    return Catalogo(canciones,[],[])