import pytest
import datetime

from codigo_TAG4 import *


# ------------------------------
# TEST Cancion
# ------------------------------

def test_creacion_cancion():
    c = Cancion(
        1,
        "Test",
        datetime.datetime.now(),
        {"ritmo":0.5,"tono":0.6,"escala":0.4},
        {"felicidad":0.7,"energia":0.3,"bailabilidad":0.8}
    )

    assert c.titulo == "Test"
    assert c.id_cancion == 1


# ------------------------------
# TEST Artista
# ------------------------------

def test_artista_atributos_medios():
    c1 = Cancion(1,"A",datetime.datetime.now(),{"ritmo":0.4,"tono":0.2,"escala":0.5},{"felicidad":0.3})
    c2 = Cancion(2,"B",datetime.datetime.now(),{"ritmo":0.6,"tono":0.4,"escala":0.7},{"felicidad":0.6})

    artista = Artista("Test",datetime.datetime(1990,1,1),[c1,c2])

    medios = artista.atributos_medios

    assert "ritmo" in medios
    assert medios["ritmo"] == pytest.approx(0.5)


def test_artista_sin_canciones():
    artista = Artista("Vacío", datetime.datetime(1990,1,1), [])
    assert artista.atributos_medios == {}


# ------------------------------
# TEST Playlist
# ------------------------------

def test_playlist_atributos_medios():
    c1 = Cancion(1,"A",datetime.datetime.now(),{"ritmo":0.2,"tono":0.2,"escala":0.3},{"felicidad":0.4})
    c2 = Cancion(2,"B",datetime.datetime.now(),{"ritmo":0.8,"tono":0.5,"escala":0.6},{"felicidad":0.7})

    playlist = Playlist("Lista",datetime.datetime.now(),[c1,c2])

    medios = playlist.atributos_medios

    assert "ritmo" in medios
    assert medios["ritmo"] == pytest.approx(0.5)


def test_playlist_vacia():
    playlist = Playlist("Vacía", datetime.datetime.now(), [])
    assert playlist.atributos_medios == {}


# ------------------------------
# TEST Catalogo
# ------------------------------

def test_buscar_cancion_catalogo():
    c = Cancion(1,"Test",datetime.datetime.now(),{"ritmo":0.5},{"felicidad":0.6})
    catalogo = Catalogo([c],[],[])

    resultado = catalogo.buscar_cancion_por_id(1)

    assert resultado.titulo == "Test"


def test_buscar_cancion_no_existe():
    catalogo = Catalogo([],[],[])

    with pytest.raises(CancionNoEncontrada):
        catalogo.buscar_cancion_por_id(99)


# ------------------------------
# TEST GENERADORES
# ------------------------------

def test_generar_atributos():
    sonoros, sentimentales = generar_atributos()

    assert "ritmo" in sonoros
    assert "felicidad" in sentimentales


def test_generar_catalogo():
    catalogo = generar_catalogo(10)

    assert len(catalogo.canciones) == 10
    assert len(catalogo.artistas) == 3
    assert len(catalogo.playlists) == 2


# ------------------------------
# TEST Singleton
# ------------------------------

def test_singleton_recomendador():
    catalogo = generar_catalogo(5)

    r1 = Recomendador.obtenerRecomendador(catalogo)
    r2 = Recomendador.obtenerRecomendador(catalogo)

    assert r1 is r2


def test_registrar_escucha():
    catalogo = generar_catalogo(5)
    r = Recomendador.obtenerRecomendador(catalogo)

    r.sesion = []

    r.registrar_escucha(0)

    assert len(r.sesion) == 1


# ------------------------------
# TEST Chain of Responsibility
# ------------------------------

def test_chain_estadisticos():
    catalogo = generar_catalogo(5)
    recomendador = Recomendador.obtenerRecomendador(catalogo)

    recomendador.sesion = catalogo.canciones[:3]

    cadena = EstadisticoSonoro(
        sucesor=EstadisticoSentimental()
    )

    cadena.manejar(recomendador.sesion)  # no debe fallar


# ------------------------------
# TEST Strategy
# ------------------------------

def test_busqueda_alfabetica():
    c1 = Cancion(1,"B",datetime.datetime.now(),{"ritmo":0.4},{"felicidad":0.5})
    c2 = Cancion(2,"A",datetime.datetime.now(),{"ritmo":0.6},{"felicidad":0.7})

    estrategia = BusquedaAlfabetica()

    resultado = estrategia.buscar([c1,c2])

    assert resultado.titulo == "A"


def test_busqueda_temporal():
    c1 = Cancion(1,"A",datetime.datetime(2020,1,1),{"ritmo":0.4},{"felicidad":0.5})
    c2 = Cancion(2,"B",datetime.datetime(2022,1,1),{"ritmo":0.6},{"felicidad":0.7})

    estrategia = BusquedaTemporal()

    resultado = estrategia.buscar([c1,c2])

    assert resultado.id_cancion == 2


def test_busqueda_aleatoria():
    c1 = Cancion(1,"A",datetime.datetime.now(),{"ritmo":0.4},{"felicidad":0.5})
    c2 = Cancion(2,"B",datetime.datetime.now(),{"ritmo":0.6},{"felicidad":0.7})

    estrategia = BusquedaAleatoria()

    resultado = estrategia.buscar([c1,c2])

    assert resultado in [c1,c2]


def test_busqueda_lista_vacia():
    estrategia = BusquedaAlfabetica()

    with pytest.raises(CatalogoVacio):
        estrategia.buscar([])


# ------------------------------
# TEST RecomendacionBase
# ------------------------------

def test_recomendacion_base_sin_sesion():
    catalogo = generar_catalogo(5)
    estrategia = BusquedaAleatoria()

    base = RecomendacionBase(catalogo, [], estrategia)

    resultado = base.recomendar()

    assert "cancion" in resultado


def test_recomendacion_base_con_sesion():
    catalogo = generar_catalogo(5)
    estrategia = BusquedaAleatoria()

    sesion = catalogo.canciones[:3]

    base = RecomendacionBase(catalogo, sesion, estrategia)

    resultado = base.recomendar()

    assert "cancion" in resultado


# ------------------------------
# TEST Decorators
# ------------------------------

def test_decorator_artista():
    catalogo = generar_catalogo(10)
    estrategia = BusquedaAleatoria()

    sesion = catalogo.canciones[:3]

    base = RecomendacionBase(catalogo, sesion, estrategia)
    decorado = DecoratorArtista(base)

    resultado = decorado.recomendar()

    assert "artista" in resultado


def test_decorator_playlist():
    catalogo = generar_catalogo(10)
    estrategia = BusquedaAleatoria()

    sesion = catalogo.canciones[:3]

    base = RecomendacionBase(catalogo, sesion, estrategia)
    decorado = DecoratorPlaylist(base)

    resultado = decorado.recomendar()

    assert "playlist" in resultado


def test_decorator_completo():
    catalogo = generar_catalogo(10)
    estrategia = BusquedaAleatoria()

    sesion = catalogo.canciones[:3]

    base = RecomendacionBase(catalogo, sesion, estrategia)
    decorado = DecoratorArtista(base)
    decorado = DecoratorPlaylist(decorado)

    resultado = decorado.recomendar()

    assert "cancion" in resultado
    assert "artista" in resultado
    assert "playlist" in resultado