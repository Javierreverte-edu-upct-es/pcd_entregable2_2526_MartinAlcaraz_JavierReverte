import random
import functools
from abc import ABCMeta, abstractmethod
import datetime


# ------------------------------
# MODELOS
# ------------------------------

class Cancion:
    def __init__(self,id_cancion,titulo,fecha_creacion,atributos_sonoros,atributos_sentimentales):
        self.id_cancion=id_cancion
        self.titulo=titulo
        self.fecha_creacion=fecha_creacion
        self.atributos_sonoros=atributos_sonoros
        self.atributos_sentimentales=atributos_sentimentales


class Artista:
    def __init__(self,nombre,fecha_nacimiento,canciones):
        self.nombre=nombre
        self.fecha_nacimiento=fecha_nacimiento
        self.canciones=canciones


class Playlist:
    def __init__(self,titulo,fecha_creacion,canciones):
        self.titulo=titulo
        self.fecha_creacion=fecha_creacion
        self.canciones=canciones


class Catalogo:
    def __init__(self,canciones,artistas,playlists):
        self.canciones=canciones
        self.artistas=artistas
        self.playlists=playlists

    def buscar_cancion_por_id(self,id_cancion):
        for c in self.canciones:
            if c.id_cancion==id_cancion:
                return c
        raise Exception("Canción no encontrada")


# ------------------------------
# GENERADOR DE CATÁLOGO
# ------------------------------

def generar_atributos():
    return {
        "ritmo":round(random.random(),2),
        "tono":round(random.random(),2),
        "escala":round(random.random(),2)
    },{
        "felicidad":round(random.random(),2),
        "energia":round(random.random(),2),
        "bailabilidad":round(random.random(),2)
    }


def generar_catalogo(n_canciones):

    canciones=[]
    for i in range(n_canciones):
        sonoros,sentimentales=generar_atributos()
        canciones.append(
            Cancion(
                i,
                f"Cancion_{i}",
                datetime.datetime.now()-datetime.timedelta(days=random.randint(1,1000)),
                sonoros,
                sentimentales
            )
        )

    artistas=[]
    for i in range(3):
        canciones_artista=random.sample(canciones,3)
        artistas.append(
            Artista(
                f"Artista_{i}",
                datetime.datetime(1980+i,1,1),
                canciones_artista
            )
        )

    playlists=[]
    for i in range(2):
        canciones_playlist=random.sample(canciones,4)
        playlists.append(
            Playlist(
                f"Playlist_{i}",
                datetime.datetime.now()-datetime.timedelta(days=random.randint(1,500)),
                canciones_playlist
            )
        )

    return Catalogo(canciones,artistas,playlists)


# ------------------------------
# R1 SINGLETON
# ------------------------------

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

    def registrar_escucha(self,id_cancion):
        cancion=self.catalogo.buscar_cancion_por_id(id_cancion)
        self.sesion.append(cancion)
        print(f"Escuchando: {cancion.titulo}")


# ------------------------------
# R2 CHAIN OF RESPONSIBILITY
# ------------------------------

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

            medias={
                k:functools.reduce(lambda a,b:a+b,map(lambda d:d[k],sonoros))/len(sonoros)
                for k in sonoros[0]
            }

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

            medias={
                k:functools.reduce(lambda a,b:a+b,map(lambda d:d[k],sentimentales))/len(sentimentales)
                for k in sentimentales[0]
            }

            desviaciones={
                k:(sum(map(lambda x:(x-medias[k])**2,map(lambda d:d[k],sentimentales)))/len(sentimentales))**0.5
                for k in sentimentales[0]
            }

            print("Media atributos sentimentales:",medias)
            print("Desviación típica atributos sentimentales:",desviaciones)

        self.pasar(sesion)


# ------------------------------
# R4 STRATEGY
# ------------------------------

class EstrategiaBusqueda(metaclass=ABCMeta):

    @abstractmethod
    def buscar(self,items):
        pass


class BusquedaAlfabetica(EstrategiaBusqueda):

    def buscar(self,items):
        return sorted(items,key=lambda x:x.titulo)[0]


class BusquedaTemporal(EstrategiaBusqueda):

    def buscar(self,items):
        return sorted(items,key=lambda x:x.fecha_creacion,reverse=True)[0]


class BusquedaAleatoria(EstrategiaBusqueda):

    def buscar(self,items):
        return random.choice(items)


# ------------------------------
# R3 DECORATOR
# ------------------------------

class RecomendacionBase:

    def __init__(self,catalogo,sesion,estrategia):
        self.catalogo=catalogo #Contiene todas las canciones, artistas y playlists.
        self.sesion=sesion  #Es la lista de canciones que el usuario ha escuchado.
        self.estrategia=estrategia  #Es el algoritmo de búsqueda elegido (patrón Strategy):

    def recomendar(self):

        # Si no hay sesión se recomienda cualquier canción
        if not self.sesion:
            cancion=self.estrategia.buscar(self.catalogo.canciones)
            return {"cancion":cancion.titulo}

        # 1️ calcular media de atributos de la sesión
        media_sonoros={
            k:sum(c.atributos_sonoros[k] for c in self.sesion)/len(self.sesion)
            for k in self.sesion[0].atributos_sonoros
        }

        media_sentimentales={
            k:sum(c.atributos_sentimentales[k] for c in self.sesion)/len(self.sesion)
            for k in self.sesion[0].atributos_sentimentales
        }

        # 2️ calcular distancia entre cada canción y la sesión
        def distancia(cancion):

            dist_sonoros=sum(
                (cancion.atributos_sonoros[k]-media_sonoros[k])**2
                for k in media_sonoros
            )

            dist_sentimentales=sum(
                (cancion.atributos_sentimentales[k]-media_sentimentales[k])**2
                for k in media_sentimentales
            )

            return (dist_sonoros+dist_sentimentales)**0.5

        # 3️ ordenar canciones por similitud
        canciones_ordenadas=sorted(self.catalogo.canciones,key=distancia)

        # 4️ aplicar strategy sobre las más similares
        cancion=self.estrategia.buscar(canciones_ordenadas)

        return {"cancion":cancion.titulo}


class DecoratorRecomendacion:

    def __init__(self,recomendacion):
        self.recomendacion=recomendacion

    @property
    def catalogo(self):
        return self.recomendacion.catalogo

    @property
    def sesion(self):
        return self.recomendacion.sesion

    @property
    def estrategia(self):
        return self.recomendacion.estrategia

    def recomendar(self):
        return self.recomendacion.recomendar()


class DecoratorArtista(DecoratorRecomendacion):

    def recomendar(self):
        resultado=super().recomendar()

        if self.catalogo.artistas:
            artista=self.estrategia.buscar(self.catalogo.artistas)
            resultado["artista"]=artista.nombre

        return resultado


class DecoratorPlaylist(DecoratorRecomendacion):

    def recomendar(self):
        resultado=super().recomendar()

        if self.catalogo.playlists:
            playlist=self.estrategia.buscar(self.catalogo.playlists)
            resultado["playlist"]=playlist.titulo

        return resultado


# ------------------------------
# EJECUCIÓN
# ------------------------------

if __name__=="__main__":

    try:

        catalogo=generar_catalogo(10)

        recomendador=Recomendador.obtenerRecomendador(catalogo)

        recomendador.registrar_escucha(1)
        recomendador.registrar_escucha(2)
        recomendador.registrar_escucha(3)

        cadena=EstadisticoSonoro(
            sucesor=EstadisticoSentimental()
        )

        cadena.manejar(recomendador.sesion)

        print("\n--- Generando recomendación ---\n")

        estrategia=BusquedaAleatoria()

        recomendacion=RecomendacionBase(
            catalogo,
            recomendador.sesion,
            estrategia
        )

        recomendacion=DecoratorArtista(recomendacion)
        recomendacion=DecoratorPlaylist(recomendacion)

        resultado=recomendacion.recomendar()

        print("Resultado recomendación:")
        print(resultado)

    except Exception as e:
        print("Error:",e)