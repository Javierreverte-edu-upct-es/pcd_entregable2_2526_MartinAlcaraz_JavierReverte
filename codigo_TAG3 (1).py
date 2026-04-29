import random
import functools
from abc import ABCMeta, abstractmethod
import datetime
import asyncio 


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
    def __init__(self, nombre, fecha_nacimiento, canciones):
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        self.canciones = canciones

    @property
    def atributos_medios(self):
        # Usamos programación funcional para promediar los diccionarios de atributos
        # Esto cumple con el requisito de "Uso de funciones de orden superior"
        if not self.canciones: return {}
        todas_caract = [c.atributos_sonoros for c in self.canciones] # O sentimentales, según se pida
        keys = todas_caract[0].keys()
        return {k: sum(c[k] for c in todas_caract) / len(todas_caract) for k in keys}

class Playlist:
    def __init__(self, titulo, fecha_creacion, canciones):
        self.titulo = titulo
        self.fecha_creacion = fecha_creacion
        self.canciones = canciones

    @property
    def atributos_medios(self):
        if not self.canciones: return {}
        todas_caract = [c.atributos_sonoros for c in self.canciones]
        keys = todas_caract[0].keys()
        return {k: sum(c[k] for c in todas_caract) / len(todas_caract) for k in keys}


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
    def buscar(self, items):
        if not items: return None
        # Corrección: Detectamos el atributo correcto según el tipo de objeto
        # Usamos una función lambda y sorted (estilo funcional)
        return sorted(
            items, 
            key=lambda x: getattr(x, 'fecha_creacion', getattr(x, 'fecha_nacimiento', None)),
            reverse=True
        )[0]


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


# CÓDIGO CORREGIDO
class DecoratorArtista(DecoratorRecomendacion):
    def recomendar(self):
        # 1. Obtenemos el diccionario base de la canción
        resultado = super().recomendar()
        
        # 2. Cálculo funcional de la media de la sesión (Requisito Funcional)
        media_sesion = 0.0
        if self.sesion:
            # Aplanamos todos los valores de atributos sonoros de todas las canciones
            valores = [val for c in self.sesion for val in c.atributos_sonoros.values()]
            if valores:
                media_sesion = sum(valores) / len(valores)

        # 3. Filtrado funcional (Requisito Funcional)
        # Filtramos artistas cuya media de sus canciones no diste más de 0.5 de la sesión
        artistas_similares = list(filter(
            lambda a: abs((sum(a.atributos_medios.values()) / len(a.atributos_medios)) - media_sesion) < 0.5 
            if a.atributos_medios else False,
            self.catalogo.artistas
        ))

        # 4. Aplicamos Strategy sobre el filtro
        if artistas_similares:
            artista = self.estrategia.buscar(artistas_similares)
            resultado["artista"] = artista.nombre
        else:
            resultado["artista"] = "No se encontraron artistas similares"
            
        return resultado
class DecoratorPlaylist(DecoratorRecomendacion):
    def recomendar(self):
        resultado = super().recomendar()
        
        # Calculamos media de sesión igual que arriba
        media_sesion = 0.0
        if self.sesion:
            valores = [val for c in self.sesion for val in c.atributos_sonoros.values()]
            if valores:
                media_sesion = sum(valores) / len(valores)

        # Filtrado de Playlists
        playlists_similares = list(filter(
            lambda p: abs((sum(p.atributos_medios.values()) / len(p.atributos_medios)) - media_sesion) < 0.5 
            if p.atributos_medios else False,
            self.catalogo.playlists
        ))

        if playlists_similares:
            playlist = self.estrategia.buscar(playlists_similares)
            resultado["playlist"] = playlist.titulo
        else:
            resultado["playlist"] = "No hay playlists similares"
            
        return resultado


# ------------------------------
# EJECUCIÓN
# ------------------------------

# 1. Creamos una función asíncrona para simular que el usuario escucha música
async def simular_escucha_real(recomendador):
    # Lista de IDs de canciones que el usuario va a oír
    canciones_a_escuchar = [1, 2, 3] 
    
    for c_id in canciones_a_escuchar:
        print(f"-> Reproduciendo canción ID: {c_id}...")
        # Registramos la escucha en el sistema
        recomendador.registrar_escucha(c_id)
        
        # 'await' pausa esta función 1 segundo (simula el tiempo real) 
        # sin detener el resto del programa
        await asyncio.sleep(1) 
    
    print("\n[INFO] Sesión de escucha completada.")

# 2. Función principal asíncrona que coordina todo el sistema
async def main():
    try:
        # Inicialización
        catalogo = generar_catalogo(20) # Aumentamos un poco para tener más variedad
        recomendador = Recomendador.obtenerRecomendador(catalogo)
        
        # R2: Concurrencia (Simulación de escucha)
        await simular_escucha_real(recomendador)
        
        # R3: Chain of Responsibility (Estadísticos)
        print("\n[PROCESANDO ESTADÍSTICOS DE SESIÓN]")
        cadena = EstadisticoSonoro(sucesor=EstadisticoSentimental())
        cadena.manejar(recomendador.sesion)
        
        print("\n--- Generando recomendación inteligente ---")
        
        # R4: Strategy
        estrategia = BusquedaTemporal() # Probamos una diferente a la aleatoria
        
        # R3: Decorator (Construcción por capas)
        # 1. Recomendación básica (Canción)
        rec_objeto = RecomendacionBase(catalogo, recomendador.sesion, estrategia)
        
        # 2. Añadimos capa de Artista
        rec_objeto = DecoratorArtista(rec_objeto)
        
        # 3. Añadimos capa de Playlist
        rec_objeto = DecoratorPlaylist(rec_objeto)
        
        # Ejecución final
        final = rec_objeto.recomendar()
        print(f"\nResultado final para el usuario:")
        for clave, valor in final.items():
            print(f" > {clave.capitalize()}: {valor}")
        
    except Exception as e:
        print(f"\n[ERROR EN EL SISTEMA]: {e}")


# 3. Punto de entrada que arranca el bucle de eventos (Event Loop)
if __name__ == "__main__":
    asyncio.run(main())
