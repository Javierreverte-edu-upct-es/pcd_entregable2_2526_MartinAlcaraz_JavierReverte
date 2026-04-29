import random
import functools
from abc import ABCMeta, abstractmethod
import datetime
import asyncio 

# ==============================================================================
# EXCEPCIONES PERSONALIZADAS
# Por qué lo hemos hecho así: En vez de que el programa explote con un error 
# raro de Python si algo falla, hemos creado nuestros propios errores. Así, si el 
# usuario busca algo que no existe, salta un mensaje claro como "El catálogo está vacío", 
# lo que nos facilita mucho encontrar dónde está el fallo.
# ==============================================================================

class CancionNoEncontrada(Exception):
    def __init__(self, mensaje="La canción no existe en el catálogo"):
        super().__init__(mensaje)

class CatalogoVacio(Exception):
    def __init__(self, mensaje="El catálogo está vacío"):
        super().__init__(mensaje)

class SesionVacia(Exception):
    def __init__(self, mensaje="La sesión de escucha está vacía"):
        super().__init__(mensaje)

class EstrategiaNoValida(Exception):
    def __init__(self, mensaje="La estrategia de búsqueda no es válida"):
        super().__init__(mensaje)


# ==============================================================================
# MODELOS DE DATOS (Las piezas de nuestro programa)
# Aquí definimos cómo es una Canción, un Artista, un Catálogo y una Playlist. 
# Hemos decidido que el Artista y la Playlist guarden dentro una lista con sus canciones.
# ==============================================================================

class Cancion:
    # El constructor guarda los datos básicos de la canción cuando la creamos.
    def __init__(self, id_cancion, titulo, fecha_creacion, atributos_sonoros, atributos_sentimentales):
        self.id_cancion = id_cancion
        self.titulo = titulo
        self.fecha_creacion = fecha_creacion
        # Estos atributos son diccionarios con valores como ritmo, energía, etc.
        self.atributos_sonoros = atributos_sonoros
        self.atributos_sentimentales = atributos_sentimentales

class Artista:
    def __init__(self, nombre, fecha_nacimiento, canciones):
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        self.canciones = canciones # Lista de objetos tipo Cancion

    # Usamos @property para poder acceder a la media de los atributos como si 
    # fuera una variable normal (ej: artista.atributos_medios) y no una función.
    @property
    def atributos_medios(self):
        # Si el artista no tiene canciones, devolvemos un diccionario vacío para que no dé error.
        if not self.canciones: return {}
        
        # Aquí usamos programación funcional. Primero sacamos una lista solo con 
        # los diccionarios de atributos sonoros de todas las canciones del artista.
        todas_caract = [c.atributos_sonoros for c in self.canciones] 
        keys = todas_caract[0].keys() # Nos guardamos las claves (ritmo, tono, escala)
        
        # Para cada clave, sumamos su valor en todas las canciones y lo dividimos 
        # entre el total de canciones para sacar la nota media.
        return {k: sum(c[k] for c in todas_caract) / len(todas_caract) for k in keys}

class Playlist:
    def __init__(self, titulo, fecha_creacion, canciones):
        self.titulo = titulo
        self.fecha_creacion = fecha_creacion
        self.canciones = canciones

    @property
    def atributos_medios(self):
        # Hacemos exactamente lo mismo que en Artista: calcular la media de las 
        # canciones de esta playlist para luego poder compararla con los gustos del usuario.
        if not self.canciones: return {}
        todas_caract = [c.atributos_sonoros for c in self.canciones]
        keys = todas_caract[0].keys()
        return {k: sum(c[k] for c in todas_caract) / len(todas_caract) for k in keys}


class Catalogo:
    # Esta clase es nuestra "Base de Datos". Lo guarda todo.
    def __init__(self, canciones, artistas, playlists):
        self.canciones = canciones
        self.artistas = artistas
        self.playlists = playlists

    def buscar_cancion_por_id(self, id_cancion):
        # Recorremos la lista de canciones una a una buscando la que coincida con el ID
        for c in self.canciones:
            if c.id_cancion == id_cancion:
                return c # Si la encontramos, la devolvemos y terminamos
        
        # Si el bucle termina y no ha encontrado nada, hacemos saltar nuestro error personalizado
        raise CancionNoEncontrada() 


# ==============================================================================
# GENERADOR DE DATOS FALSOS (Para probar el programa)
# ==============================================================================

def generar_atributos():
    # Nos inventamos números decimales aleatorios entre 0 y 1 para los atributos musicales
    return {
        "ritmo": round(random.random(), 2),
        "tono": round(random.random(), 2),
        "escala": round(random.random(), 2)
    }, {
        "felicidad": round(random.random(), 2),
        "energia": round(random.random(), 2),
        "bailabilidad": round(random.random(), 2)
    }

def generar_catalogo(n_canciones):
    canciones = []
    # Generamos tantas canciones falsas como nos pidan en 'n_canciones'
    for i in range(n_canciones):
        sonoros, sentimentales = generar_atributos()
        canciones.append(
            Cancion(
                i,
                f"Cancion_{i}",
                # Le restamos días aleatorios a la fecha de hoy para simular que son antiguas
                datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 1000)),
                sonoros,
                sentimentales
            )
        )

    artistas = []
    # Creamos 3 artistas y a cada uno le damos 3 canciones al azar de la lista que acabamos de crear
    for i in range(3):
        canciones_artista = random.sample(canciones, 3)
        artistas.append(
            Artista(f"Artista_{i}", datetime.datetime(1980 + i, 1, 1), canciones_artista)
        )

    playlists = []
    # Creamos 2 playlists, con 4 canciones al azar cada una
    for i in range(2):
        canciones_playlist = random.sample(canciones, 4)
        playlists.append(
            Playlist(f"Playlist_{i}", datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 500)), canciones_playlist)
        )

    # Devolvemos el catálogo ya montado con toda la información
    return Catalogo(canciones, artistas, playlists)


# ==============================================================================
# REQUISITO 1: PATRÓN SINGLETON (El Recomendador)
# Por qué lo usamos: Solo queremos que exista un único Recomendador abierto. Si 
# creáramos varios, cada uno tendría un historial (sesión) diferente y perderíamos 
# la cuenta de qué música está escuchando realmente el usuario.
# ==============================================================================

class Recomendador:
    # Esta variable de clase guarda al único recomendador que se va a crear.
    _instancia = None 

    @classmethod
    def obtenerRecomendador(cls, catalogo):
        # Si _instancia está vacía (es la primera vez que entramos), creamos el objeto.
        # Si ya tiene algo, simplemente devolvemos ese algo. Así evitamos duplicados.
        if not cls._instancia:
            cls._instancia = cls(catalogo)
        return cls._instancia

    def __init__(self, catalogo):
        self.catalogo = catalogo
        # La 'sesion' es como nuestro carrito de la compra: guarda lo que vamos escuchando
        self.sesion = [] 

    def registrar_escucha(self, id_cancion):
        # Cuando el usuario escucha algo, lo buscamos en el catálogo y lo guardamos en su sesión
        cancion = self.catalogo.buscar_cancion_por_id(id_cancion)
        self.sesion.append(cancion)
        print(f"Escuchando: {cancion.titulo}")


# ==============================================================================
# REQUISITO 2: PATRÓN CHAIN OF RESPONSIBILITY (La cadena de estadísticas)
# Por qué lo usamos: Imagina una fábrica en línea. El primer trabajador (Sonoro)
# hace sus cálculos estadísticos y, cuando termina, le pasa el paquete al 
# siguiente trabajador (Sentimental) automáticamente. Si en el futuro queremos 
# añadir otro paso, solo lo enganchamos al final de la cadena sin tocar lo anterior.
# ==============================================================================

class Handler:
    def __init__(self, sucesor=None):
        # Cada eslabón guarda quién es el siguiente en la cadena ('sucesor')
        self.sucesor = sucesor 

    def manejar(self, sesion):
        pass # Los hijos pondrán aquí su código

    def pasar(self, sesion):
        # Si tengo un compañero después de mí, le paso los datos para que trabaje él.
        if self.sucesor:
            self.sucesor.manejar(sesion)


class EstadisticoSonoro(Handler):
    def manejar(self, sesion):
        # REQUISITO: Uso de Programación Funcional. 
        # map y lambda cogen la lista de canciones y extraen solo la parte de atributos sonoros.
        sonoros = list(map(lambda c: c.atributos_sonoros, sesion))

        if sonoros:
            # functools.reduce suma todos los valores y luego dividimos por la cantidad (media)
            medias = {
                k: functools.reduce(lambda a, b: a + b, map(lambda d: d[k], sonoros)) / len(sonoros)
                for k in sonoros[0]
            }

            # Fórmula matemática de la desviación típica aplicada usando sum() y map()
            desviaciones = {
                k: (sum(map(lambda x: (x - medias[k])**2, map(lambda d: d[k], sonoros))) / len(sonoros))**0.5
                for k in sonoros[0]
            }

            print("Media atributos sonoros:", medias)
            print("Desviación típica atributos sonoros:", desviaciones)

        # Cuando termino de calcular, le digo a la cadena que siga avanzando
        self.pasar(sesion)


class EstadisticoSentimental(Handler):
    def manejar(self, sesion):
        # Hace el mismo proceso que el anterior, pero enfocado en la parte sentimental (energía, etc.)
        
        sentimentales = list(map(lambda c: c.atributos_sentimentales, sesion))

        if sentimentales:
            medias = {
                k: functools.reduce(lambda a, b: a + b, map(lambda d: d[k], sentimentales)) / len(sentimentales)
                for k in sentimentales[0]
            }

            desviaciones = {
                k: (sum(map(lambda x: (x - medias[k])**2, map(lambda d: d[k], sentimentales))) / len(sentimentales))**0.5
                for k in sentimentales[0]
            }

            print("Media atributos sentimentales:", medias)
            print("Desviación típica atributos sentimentales:", desviaciones)

        self.pasar(sesion)


# ==============================================================================
# REQUISITO 4: PATRÓN STRATEGY (Formas de buscar recomendación)
# Por qué lo usamos: Nos permite crear diferentes reglas o "estrategias" de búsqueda 
# (por orden alfabético, por fecha o al azar) y cambiar entre ellas cuando queramos, 
# sin tener que modificar la clase principal que hace la recomendación.
# ==============================================================================

class EstrategiaBusqueda(metaclass=ABCMeta):
    # Esta es la clase padre. Obliga a que todas las estrategias que creemos tengan la función 'buscar'
    @abstractmethod
    def buscar(self, items):
        pass

class BusquedaAlfabetica(EstrategiaBusqueda):
    def buscar(self, items):
        if not items: raise CatalogoVacio("Lista vacía para búsqueda alfabética")
        # sorted() ordena alfabéticamente mirando el '.titulo'. Devolvemos el primero ([0]).
        return sorted(items, key=lambda x: x.titulo)[0]

class BusquedaTemporal(EstrategiaBusqueda):
    def buscar(self, items):
        if not items: raise CatalogoVacio("Lista vacía para búsqueda temporal")
        # Aquí usamos un truco: 'getattr' intenta buscar la fecha de creación (canciones/playlists).
        # Si no la encuentra, intenta buscar la fecha de nacimiento (artistas).
        # reverse=True hace que nos devuelva primero lo más reciente.
        return sorted(
            items, 
            key=lambda x: getattr(x, 'fecha_creacion', getattr(x, 'fecha_nacimiento', None)),
            reverse=True
        )[0]

class BusquedaAleatoria(EstrategiaBusqueda):
    def buscar(self, items):
        if not items: raise CatalogoVacio("No hay elementos para buscar")
        # Elige uno al azar de la lista
        return random.choice(items)


# ==============================================================================
# REQUISITO 3: PATRÓN DECORATOR (Añadir recomendaciones como capas de cebolla)
# Por qué lo usamos: Para no crear una superclase gigante. Empezamos con una base 
# que solo recomienda una Canción. Luego la "envolvemos" con un decorador que le 
# pega un Artista sugerido al resultado. Luego la envolvemos otra vez para pegarle 
# una Playlist. Así, el diccionario final va creciendo capa por capa.
# ==============================================================================

class RecomendacionBase:
    def __init__(self, catalogo, sesion, estrategia):
        # Necesita conocer todas las canciones, lo que ha escuchado el usuario y cómo buscar
        self.catalogo = catalogo 
        self.sesion = sesion 
        self.estrategia = estrategia 

    def recomendar(self):
        # Si el usuario es nuevo y no ha escuchado nada, le recomendamos algo genérico
        if not self.sesion:
            cancion = self.estrategia.buscar(self.catalogo.canciones)
            return {"cancion": cancion.titulo} # Devuelve un diccionario simple

        # 1. Calculamos cómo es el gusto medio del usuario en base a lo que ha escuchado
        media_sonoros = {k: sum(c.atributos_sonoros[k] for c in self.sesion) / len(self.sesion) for k in self.sesion[0].atributos_sonoros}
        media_sentimentales = {k: sum(c.atributos_sentimentales[k] for c in self.sesion) / len(self.sesion) for k in self.sesion[0].atributos_sentimentales}

        # 2. Creamos una función matemática para ver cuánto se parece cada canción del catálogo a los gustos del usuario
        def distancia(cancion):
            dist_sonoros = sum((cancion.atributos_sonoros[k] - media_sonoros[k])**2 for k in media_sonoros)
            dist_sentimentales = sum((cancion.atributos_sentimentales[k] - media_sentimentales[k])**2 for k in media_sentimentales)
            return (dist_sonoros + dist_sentimentales)**0.5 # Distancia euclídea

        # 3. Ordenamos todo el catálogo de música. Las primeras de la lista serán las que más se parezcan a su gusto.
        canciones_ordenadas = sorted(self.catalogo.canciones, key=distancia)

        # 4. Le pasamos esta lista ordenada a nuestra estrategia (ej: que elija la más moderna de las similares)
        cancion = self.estrategia.buscar(canciones_ordenadas)

        # Devolvemos el diccionario inicial que luego los decoradores irán rellenando
        return {"cancion": cancion.titulo}


class DecoratorRecomendacion:
    # Esta es la cáscara del decorador. Guarda dentro al objeto que estamos envolviendo.
    def __init__(self, recomendacion):
        self.recomendacion = recomendacion

    # Redirigimos el catálogo, sesión y estrategia hacia el objeto que tenemos dentro
    # para poder seguir usando esos datos sin tener que copiarlos.
    @property
    def catalogo(self): return self.recomendacion.catalogo
    @property
    def sesion(self): return self.recomendacion.sesion
    @property
    def estrategia(self): return self.recomendacion.estrategia

    def recomendar(self):
        return self.recomendacion.recomendar()


class DecoratorArtista(DecoratorRecomendacion):
    def recomendar(self):
        # 1. Al usar super().recomendar(), le decimos a la recomendación que tenemos 
        # envuelta: "oye, dame tu diccionario". Aquí 'resultado' será algo como {"cancion": "Cancion 5"}.
        resultado = super().recomendar()
        
        # 2. Calculamos la nota media de todos los atributos sonoros que el usuario ha escuchado
        media_sesion = 0.0
        if self.sesion:
            valores = [val for c in self.sesion for val in c.atributos_sonoros.values()]
            if valores: media_sesion = sum(valores) / len(valores)

        # 3. PROGRAMACIÓN FUNCIONAL: Usamos 'filter' y una función 'lambda' (anónima).
        # Vamos artista por artista comprobando si la nota media de su música se parece 
        # (diferencia menor a 0.5 puntos) a lo que le gusta al usuario.
        artistas_similares = list(filter(
            lambda a: abs((sum(a.atributos_medios.values()) / len(a.atributos_medios)) - media_sesion) < 0.5 
            if a.atributos_medios else False,
            self.catalogo.artistas
        ))

        # 4. Si encontramos artistas afines, le pasamos la lista a la estrategia,
        # cogemos el ganador y SE LO AÑADIMOS al diccionario que teníamos antes.
        if artistas_similares:
            artista = self.estrategia.buscar(artistas_similares)
            resultado["artista"] = artista.nombre # Añadimos la clave "artista"
        else:
            resultado["artista"] = "No se encontraron artistas similares"
            
        return resultado # Devolvemos el diccionario, que ahora tiene 2 cosas (cancion y artista)


class DecoratorPlaylist(DecoratorRecomendacion):
    def recomendar(self):
        # 1. Llamamos a lo que haya debajo. Como tenemos una muñeca rusa, esto llamará al 
        # DecoratorArtista, que llamará a la Base. Al final 'resultado' vuelve con Canción y Artista.
        resultado = super().recomendar()
        
        # 2. Hacemos el mismo cálculo de nota media del usuario
        media_sesion = 0.0
        if self.sesion:
            valores = [val for c in self.sesion for val in c.atributos_sonoros.values()]
            if valores: media_sesion = sum(valores) / len(valores)

        # 3. Filtramos las playlists comprobando si su media musical encaja con el usuario
        playlists_similares = list(filter(
            lambda p: abs((sum(p.atributos_medios.values()) / len(p.atributos_medios)) - media_sesion) < 0.5 
            if p.atributos_medios else False,
            self.catalogo.playlists
        ))

        # 4. Elegimos la playlist según la estrategia y la añadimos como tercera clave al diccionario
        if playlists_similares:
            playlist = self.estrategia.buscar(playlists_similares)
            resultado["playlist"] = playlist.titulo
        else:
            resultado["playlist"] = "No hay playlists similares"
            
        return resultado # Devolvemos el diccionario completo final


# ==============================================================================
# EJECUCIÓN DEL PROGRAMA (CONCURRENCIA)
# Por qué lo usamos: Queremos imitar el comportamiento de una app real como Spotify. 
# En vez de escuchar 3 canciones en 0.001 segundos, obligamos al programa a "esperar" 
# usando asyncio.sleep(), permitiendo que otras partes del sistema funcionen mientras tanto.
# ==============================================================================

# Definimos la función con 'async def' para poder usar pausas asíncronas
async def simular_escucha_real(recomendador):
    canciones_a_escuchar = [1, 2, 3] 
    
    for c_id in canciones_a_escuchar:
        print(f"-> Reproduciendo canción ID: {c_id}...")
        recomendador.registrar_escucha(c_id) # Guardamos la canción en la sesión
        
        # 'await asyncio.sleep(1)' pausa la ejecución 1 segundo simulando tiempo real, 
        # pero a diferencia de time.sleep(), no bloquea toda la CPU.
        await asyncio.sleep(1) 
    
    print("\n[INFO] Sesión de escucha completada.")


async def main():
    try:
        # 1. Cargamos nuestra base de datos falsa
        catalogo = generar_catalogo(20) 
        if not catalogo.canciones: raise CatalogoVacio("El catálogo no contiene canciones")
        
        # 2. Llamamos al motor Singleton. Solo habrá uno en toda la ejecución.
        recomendador = Recomendador.obtenerRecomendador(catalogo)
        
        # 3. Arrancamos la simulación asíncrona (el usuario escucha música)
        await simular_escucha_real(recomendador)
        
        # 4. Iniciamos la Cadena de Estadísticos. 
        # Solo le decimos al Sonoro que arranque, y él se encargará de pasarle el testigo al Sentimental.
        print("\n[PROCESANDO ESTADÍSTICOS DE SESIÓN]")
        cadena = EstadisticoSonoro(sucesor=EstadisticoSentimental())

        if not recomendador.sesion: raise SesionVacia("El usuario no ha escuchado canciones")
        cadena.manejar(recomendador.sesion) 
        
        print("\n--- Generando recomendación inteligente ---")
        
        # 5. Elegimos la Estrategia. Si quisiéramos cambiarla, solo cambiaríamos esta línea.
        estrategia = BusquedaTemporal() 
        
        # 6. Montamos el Recomendador con los Decoradores (Capas).
        # Primero la base.
        rec_objeto = RecomendacionBase(catalogo, recomendador.sesion, estrategia)
        # Luego la envolvemos en Artista.
        rec_objeto = DecoratorArtista(rec_objeto)
        # Por último, envolvemos todo en Playlist.
        rec_objeto = DecoratorPlaylist(rec_objeto)
        
        # 7. Disparamos el cálculo final. Esto atravesará todas las capas de fuera a dentro y de dentro a fuera.
        final = rec_objeto.recomendar()
        
        # Mostramos los resultados finales limpios por pantalla
        print(f"\nResultado final para el usuario:")
        for clave, valor in final.items():
            print(f" > {clave}: {valor}")
        
    # Si en algún momento salta un error, caerá en su bloque correspondiente y no romperá el programa feamente
    except CatalogoVacio as e:
        print("[ERROR CATÁLOGO]:", e)
    except SesionVacia as e:
        print("[ERROR SESIÓN]:", e)
    except Exception as e:
        print("[ERROR GENERAL]:", e)

# Este es el punto de inicio de Python. Arranca el "bucle de eventos" necesario para usar funciones async
if __name__ == "__main__":
    asyncio.run(main())