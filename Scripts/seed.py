from database import get_session
from models import Categoria, Libro
from scraper import scraping
from sqlmodel import select


# Ingresa datos en la base de datos
def poblar_base_de_datos() -> None:
    print("\nRealizando scraping de la página")
    libros_scrapeados = scraping()

    # Si mo se scrapeó ningún libro
    if not libros_scrapeados:
        print("No se obtuvieron datos.")
        return

    print(f"\nInsertando {len(libros_scrapeados)} registros en la base de datos...")

    session_gen = get_session()
    session = next(session_gen)

    try:
        # Antes de insertar un libro,
        # se asegura de que la categoría ya existe en la base de datos

        # Diccionario que recuerda qué categorías ya se procesaron
        # Relaciona categoria y su id
        categorias_procesadas: dict[str, int] = {}

        for datos_libro in libros_scrapeados:
            nombre_categoria = datos_libro["categoria"]

            # Si la categoría no ha sido procesada anteriormente
            if nombre_categoria not in categorias_procesadas:
                # Busca si la categoría esta en la base de datos
                busqueda = select(Categoria).where(Categoria.nombre == nombre_categoria)
                db_categoria = session.exec(busqueda).first()

                if db_categoria:
                    # Si ya existía en la bd, guarda su id
                    categorias_procesadas[nombre_categoria] = db_categoria.id
                else:
                    # Si no existía, la crea y guarda su id
                    nueva_cat = Categoria(nombre=nombre_categoria)
                    session.add(nueva_cat)
                    session.flush()
                    categorias_procesadas[nombre_categoria] = nueva_cat.id

            # id del libro
            id_categoria_asignada = categorias_procesadas[nombre_categoria]

            # Verifica si el libro ya existe en la base de datos
            busqueda_libro = select(Libro).where(Libro.titulo == datos_libro["titulo"])
            db_libro = session.exec(busqueda_libro).first()

            if db_libro:
                print(f"{datos_libro['titulo']} ya existe en la base de datos")
                continue

            # Inserta el libro con sus datos
            nuevo_libro = Libro(
                titulo=datos_libro["titulo"],
                precio=datos_libro["precio"],
                valoracion=datos_libro["valoracion"],
                disponible=datos_libro["disponible"],
                url_detalle=datos_libro["url_detalle"],
                categoria_id=id_categoria_asignada,
            )
            session.add(nuevo_libro)

        session.commit()
        print("\nTodos los datos han sido almacenados correctamente en data.db")

    except Exception as error:
        print(f"\nOcurrió un error durante la inserción: {error}")
        session.rollback()

    finally:
        session.close()