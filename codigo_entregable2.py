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

# R1 SINGLETON -> Solo debe haber un único objeto recomendador.
class Recomendador:
    _instancia=None
    @classmethod
    def obtenerRecomendador(cls,catalogo):
        if not cls._instancia:
            cls._instancia=cls(catalogo)
        return cls._instancia
    def __init__(self,catalogo):
        self.catalogo=catalogo
        self.sesion=[]
    def registrar_escucha(self,id_cancion):  #Cada vez que el usuario escucha una canción se actualiza la sesión.
        cancion=self.catalogo.buscar_cancion_por_id(id_cancion)
        self.sesion.append(cancion)
        print(f"Escuchando: {cancion.titulo}")

# R2 CHAIN OF RESPONSIBILITY
class Handler:
    def __init__(self,sucesor=None):
        self.sucesor=sucesor
    def manejar(self,sesion):
        pass
    def pasar(self,sesion):
        if self.sucesor:
            self.sucesor.manejar(sesion)

class EstadisticoSonoro(Handler):
    def manejar(self,sesion):
        sonoros=list(map(lambda c:c.atributos_sonoros,sesion))
        if sonoros:
            medias={k:functools.reduce(lambda a,b:a+b,map(lambda d:d[k],sonoros))/len(sonoros) for k in sonoros[0]}
            desviaciones={
                k:(sum(map(lambda x:(x-medias[k])**2,map(lambda d:d[k],sonoros)))/len(sonoros))**0.5
                for k in sonoros[0]
            }
            print("Media atributos sonoros:",medias)
            print("Desviación típica atributos sonoros:",desviaciones)
        self.pasar(sesion)

class EstadisticoSentimental(Handler):
    def manejar(self,sesion):
        sentimentales=list(map(lambda c:c.atributos_sentimentales,sesion))
        if sentimentales:
            medias={k:functools.reduce(lambda a,b:a+b,map(lambda d:d[k],sentimentales))/len(sentimentales) for k in sentimentales[0]}
            desviaciones={
                k:(sum(map(lambda x:(x-medias[k])**2,map(lambda d:d[k],sentimentales)))/len(sentimentales))**0.5
                for k in sentimentales[0]
            }
            print("Media atributos sentimentales:",medias)
            print("Desviación típica atributos sentimentales:",desviaciones)
        self.pasar(sesion)

# R4 STRATEGY (Buscar desde el más reciente al más antiguo)
class EstrategiaBusqueda(metaclass=ABCMeta):
    @abstractmethod
    def buscar(self,items):
        pass

class BusquedaAlfabetica(EstrategiaBusqueda):
    def buscar(self,items):
        return sorted(items,key=lambda x:x.titulo)

class BusquedaTemporal(EstrategiaBusqueda):
    def buscar(self,items):
        return sorted(items,key=lambda x:x.fecha_creacion,reverse=True)

class BusquedaAleatoria(EstrategiaBusqueda):
    def buscar(self,items):
        return random.sample(items,len(items))
    
# R3 DECORATOR (Por defecto se recomiendan canciones pero el usuario puede pedir artistas o playlists)
class RecomendacionBase:
    def recomendar(self):
        print("Recomendando canciones")

class DecoratorRecomendacion:
    def __init__(self,recomendacion):
        self.recomendacion=recomendacion
    def recomendar(self):
        self.recomendacion.recomendar()

class DecoratorArtista(DecoratorRecomendacion):
    def recomendar(self):
        super().recomendar()
        print("Recomendando artistas")

class DecoratorPlaylist(DecoratorRecomendacion):
    def recomendar(self):
        super().recomendar()
        print("Recomendando playlists")