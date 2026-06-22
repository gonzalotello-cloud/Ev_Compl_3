from database import crear_tablas, get_session
from queries import estadisticas, items_por_categoria, top_10_por_criterio, total_items
from seed import poblar_base_de_datos


# Orquesta el pipeline completo
def main() -> None:
    # Crea las tablas en la base de datos
    print("- Creando tablas -")
    crear_tablas()

    # Ejecuta scraping y persiste los datos
    print("\n- Scraping y persistencia -")
    poblar_base_de_datos()

    # Ejecuta consultas de verificación
    print("\n-Consultas de verificación -")

    session_gen = get_session()
    session = next(session_gen)

    try:
        # Consulta 1 — Total de items almacenados
        print("\n- Consulta 1: Total de ítems almacenados -")
        total = total_items(session)
        print(f"Total de libros en la base de datos: {total}")

        # Consulta 2 — Libros por categoría
        print("\n- Consulta 2: Libros por categoría -")
        por_categoria = items_por_categoria(session)
        for nombre, cantidad in por_categoria:
            print(f"  {nombre:<30} {cantidad:>2} libro(s)")

        # Consulta 3 — Top 10 libros más caros
        print("\n- Consulta 3: Top 10 libros por precio -")
        top_10 = top_10_por_criterio(session)
        for i, libro in enumerate(top_10, start=1):
            print(f"  {i:>2}. £{libro.precio:>6.2f}  {libro.titulo}")

        # Consulta 4 — Estadísticas descriptivas de precio
        print("\n- Consulta 4: Estadísticas de precio -")
        stats = estadisticas(session)
        stats_global = stats["global"]
        print(f"  {'Global':<28} prom £{stats_global['promedio']:>6.2f}  min £{stats_global['minimo']:>6.2f}  max £{stats_global['maximo']:>6.2f}\n")
        for categoria in stats["por_categoria"]:
            print(
                f"  {categoria['categoria']:<28} "
                f"prom £{categoria['promedio']:>6.2f}  "
                f"min £{categoria['minimo']:>6.2f}  "
                f"max £{categoria['maximo']:>6.2f}"
            )

    finally:
        session.close()

if __name__ == "__main__":
    main()