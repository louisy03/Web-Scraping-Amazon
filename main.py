from bs4 import BeautifulSoup
import urllib.request
import json
import random
import time
from datetime import datetime

# Lista de User-Agents para rotar en cada solicitud
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.88 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.88 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6053.10 Safari/537.36"
]

# Función para extraer el título del producto
def get_title(soup):
    try:
        title = soup.find("span", attrs={"id": 'productTitle'}).text.strip()
    except AttributeError:
        title = ""
    return title

# Función para extraer el precio del producto
def get_price(soup):
    try:
        # Buscar el precio entero y los decimales
        price_whole = soup.find("span", attrs={'class': 'a-price-whole'}).text.strip()
        price_fraction = soup.find("span", attrs={'class': 'a-price-fraction'}).text.strip()
        price = f"MXN ${price_whole}{price_fraction}"
    except AttributeError:
        price = " No Price Specified"
    return price

# Función para extraer la calificación del producto
def get_rating(soup):
    try:
        rating = soup.find("span", attrs={'class': 'a-icon-alt'}).text.strip()
    except AttributeError:
        rating = "No Rating"
    return rating

# Función para extraer el número de reseñas
def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id': 'acrCustomerReviewText'}).text.strip()
    except AttributeError:
        review_count = "No Reviews"
    return review_count

# Función para extraer la disponibilidad
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'}).find("span").text.strip()
    except AttributeError:
        available = "Not Available"
    return available

# Función para realizar solicitudes HTTP con urllib
def fetch_url(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.read()

# Función para verificar si la página contiene un CAPTCHA
def is_captcha_page(soup):
    return soup.find("form", attrs={"action": "/errors/validateCaptcha"}) is not None

if __name__ == '__main__':
    # URL inicial
    URL = "https://www.amazon.com.mx/s?k=disco+eminem"

    # Selección de un User-Agent al azar
    HEADERS = {
        'User-Agent': random.choice(USER_AGENTS),
    }

    # Realizar la solicitud HTTP
    try:
        webpage_content = fetch_url(URL, HEADERS)
    except urllib.error.URLError as e:
        print(f"Error al realizar la solicitud: {e}")
        exit()

    # Crear el objeto Soup
    soup = BeautifulSoup(webpage_content, "html.parser")

    # Verificar si la página contiene CAPTCHA
    if is_captcha_page(soup):
        print("Se encontró un CAPTCHA. No se puede continuar.")
        exit()

    # Extraer los enlaces de productos
    links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})
    links_list = [link.get('href') for link in links]

    # Lista para almacenar los datos
    data = []

    # Iterar sobre los enlaces
    for link in links_list:
        product_url = "https://www.amazon.com.mx" + link

        # Rotar User-Agent en cada solicitud
        HEADERS['User-Agent'] = random.choice(USER_AGENTS)

        # Hacer la solicitud
        try:
            product_content = fetch_url(product_url, HEADERS)
        except urllib.error.URLError as e:
            print(f"Error al obtener el producto: {e}")
            continue

        product_soup = BeautifulSoup(product_content, "html.parser")

        # Verificar si la página contiene CAPTCHA
        if is_captcha_page(product_soup):
            print(f"CAPTCHA detectado al intentar acceder a: {product_url}. Saltando.")
            continue
        
        # Verificar si el titulo esta en blanco, saltar el producto
        title = get_title(product_soup)
        
        if title == "":
            continue
        else:
            # Extraer información del producto y agregarla a la lista
            product_data = {
                'title': title,
                'price': get_price(product_soup),
                'rating': get_rating(product_soup),
                'reviews': get_review_count(product_soup),
                'availability': get_availability(product_soup)
            }

        # Agregar solo si los datos son válidos
        if any(product_data.values()):
            data.append(product_data)

        # Pausa entre solicitudes
        delay = random.uniform(5, 15)  # Ajuste para pausas más humanas
        print(f"Esperando {delay:.2f} segundos...")
        time.sleep(delay)

    # Guardar los datos en un archivo JSON
    if data:  # Verificar si hay datos antes de intentar guardar
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"amazon_data_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Datos guardados en: {filename}")
    else:
        print("No se encontraron datos válidos para guardar.")