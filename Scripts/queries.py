from sqlmodel import Session, func, select

from models import Categoria, Libro

# Consultas de verificación

def total_items(session: Session) -> int:
    # Retorna el número total de items almacenados en la base de datos
    resultado: int = session.exec(select(func.count()).select_from(Libro)).one()
    return resultado


def items_por_categoria(session: Session) -> list[tuple[str, int]]:
    # Retorna cada categoría y su cantidad de items, ordenado de mayor a menor
    query = (
        select(Categoria.nombre, func.count(Libro.id).label("total"))
        .join(Libro, Libro.categoria_id == Categoria.id)
        .group_by(Categoria.nombre)
        .order_by(func.count(Libro.id).desc())
    )
    resultados = session.exec(query).all()
    return [(nombre, total) for nombre, total in resultados]


def top_10_por_criterio(session: Session) -> list[Libro]:
    # Retorna los 10 libros con el precio más alto
    query = select(Libro).order_by(Libro.precio.desc()).limit(10)
    return list(session.exec(query).all())


def estadisticas(session: Session) -> dict:
    # Retorna promedio, mínimo y máximo de precio, tanto global como por categoría
    # Estadísticas globales
    query_global = select(
        func.avg(Libro.precio).label("promedio"),
        func.min(Libro.precio).label("minimo"),
        func.max(Libro.precio).label("maximo"),
    )
    promedio: float
    minimo: float
    maximo: float
    promedio, minimo, maximo = session.exec(query_global).one()

    # Estadísticas por categoría
    query_categoria = (
        select(
            Categoria.nombre,
            func.avg(Libro.precio).label("promedio"),
            func.min(Libro.precio).label("minimo"),
            func.max(Libro.precio).label("maximo"),
        )
        .join(Libro, Libro.categoria_id == Categoria.id)
        .group_by(Categoria.nombre)
        .order_by(Categoria.nombre)
    )
    categorias = session.exec(query_categoria).all()

    return {
        "global": {
            "promedio": round(promedio, 2),
            "minimo": minimo,
            "maximo": maximo,
        },
        "por_categoria": [
            {
                "categoria": nombre,
                "promedio": round(avg, 2),
                "minimo": mn,
                "maximo": mx,
            }
            for nombre, avg, mn, mx in categorias
        ],
    }

