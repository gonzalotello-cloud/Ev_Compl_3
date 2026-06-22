from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scraping() -> list[dict]:
    # Configura opciones
    options = Options()
    options.add_argument('--headless') # sin ventana visible

    # Configura servicio
    service = Service(ChromeDriverManager().install())

    # Crea driver
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, timeout=10)

    # Se scrapeará books.toscrape.com
    driver.get('https://books.toscrape.com/index.html')

    # Navega desde el home a la categoría "Books" mediante un click

    # Busca cualquier enlace que esté dentro de una lista que tenga la clase nav-list
    # De esta forma se asegura que la barra lateral esté cargada antes de continuar
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.nav-list a")))
    # Busca el enlace de "Books" de la barra lateral
    catalogo = driver.find_element(By.LINK_TEXT, "Books")
    # Almacena el url actual
    url_home: str = driver.current_url
    # Clikea en boton "Books"
    catalogo.click()
    # Pausa la ejecución hasta que la URL del navegador sea distinta a url_home
    wait.until(EC.url_changes(url_home))


    # Diccionario para mapear las valoraciones de cada libro
    word_to_num: dict[str, int] = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    TOTAL_LIBROS: int = 50
    libros_scrapeados: int = 0
    libros_resultados: list[dict] = []

    # Se scrapean 50 libros
    while libros_scrapeados < TOTAL_LIBROS:
        # Espera a que todos los enlaces de libros hayan cargado antes de continuar
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a:has(img.thumbnail)")))
        # Guarda url actual, Se usará para poder volver a la pagina actual
        url_pagina_actual: str = driver.current_url

        # Encuentra todos los elementos con portada en la página y los guarda como una lista de objetos Selenium.
        libros_en_pagina = driver.find_elements(By.CSS_SELECTOR, "a:has(img.thumbnail)")
        # Recorre la lista anterior y extrae la url de cada libro de la pagina
        urls_pagina: list[str] = [libro.get_attribute("href") for libro in libros_en_pagina]

        for url_libro in urls_pagina:
            if libros_scrapeados >= TOTAL_LIBROS:
                break

            print(f" - Extrayendo Libro {libros_scrapeados + 1} de {TOTAL_LIBROS} -")

            # Vuelve a la página del catálogo antes de cada libro
            driver.get(url_pagina_actual)
            try:
                # Espera hasta que el enlace del libro sea clickeable
                enlace = wait.until(
                    # Divide la url del libro en partes, usando / como separador
                    # Toma el penultimo elemento: el identificador del libro
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href*='{url_libro.split('/')[-2]}']")))
                # Ingresa al enlace a través de un click
                enlace.click()
            except Exception:
                # Si el click falla, navega directamente a la url del libro
                driver.get(url_libro)  # Fallback directo si falla el clic

            # Diccionario temporal para el ítem actual con valores por defecto
            item: dict = {
                "titulo": "N/A",
                "precio": 0.0,
                "valoracion": 0,
                "disponible": False,
                "url_detalle": url_libro,
                "categoria": "No_Especifica"
            }

            # Extrae el titulo del libro
            try:
                item["titulo"] = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h1"))).text
            except Exception as e:
                print(f"Error título: {e}")

            # Extrae la valoración del libro
            try:
                get_valoracion: str = driver.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class")
                # Tranforma el texto de valoración de la página en número
                item["valoracion"] = word_to_num.get(get_valoracion.split()[1], 0)
            except Exception as e:
                print(f"Error valoración: {e}")

            # Extrae el precio del libro
            try:
                get_precio: str = driver.find_element(By.CLASS_NAME, "price_color").text
                cleaned_str: str = get_precio.replace("£", "").replace("Â", "").strip()
                item["precio"] = float(cleaned_str)
            except Exception as e:
                print(f"Error precio: {e}")

            # Extrae la categoria del libro
            try:
                # Se extrae el tercer texto del breadcrumb
                get_categoria = driver.find_element(By.XPATH, "//ul[@class='breadcrumb']/li[3]/a")
                item["categoria"] = get_categoria.text.strip()
            except Exception as e:
                print(f"Error categoría: {e}")

            # Extrae la disponibilidad del libro
            try:
                get_disponible = driver.find_element(By.XPATH, "//th[text()='Availability']/following-sibling::td")
                # Si Availability = In stock se almacena True, False en caso contrario
                item["disponible"] = "In stock" in get_disponible.text
            except Exception as e:
                print(f"Error disponibilidad: {e}")

            # Agrega el libro a los resultados
            libros_resultados.append(item)
            libros_scrapeados += 1

        # Si despues de recorrer toda la pagina aun no se han scrapeado 50 libros
        # Entonces, se va a la siguiente pagina del catalogo
        if libros_scrapeados < TOTAL_LIBROS:
            try:
                # Vuelve a la página del catálogo que estaba procesando
                driver.get(url_pagina_actual)
                # Espera a que los libros de la página sean visibles antes de continuar.
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a:has(img.thumbnail)")))
                # Guarda la url actual antes de hacer click en "next"
                url_antes: str = driver.current_url
                # Busca el botón "next" y espera a que esté listo para clickear.
                siguiente = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next a")))
                # Clickea boton "next"
                siguiente.click()
                # Pausa la ejecución hasta que la url cambie respecto a url_antes
                # Asegurandose de que el loop funcione correctamente al cambiar pagina
                wait.until(EC.url_changes(url_antes))
                time.sleep(1.0)  # sleep de cortesía por página

            except Exception:
                print("No hay más páginas disponibles en el catálogo.")
                break

    # Cierra el driver y retorna los resultados
    driver.quit()
    return libros_resultados