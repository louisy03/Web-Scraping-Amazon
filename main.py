import csv
import json
from bs4 import BeautifulSoup
import urllib.request
import random
import time
from datetime import datetime

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

def get_title(soup):
    try:
        title = soup.find("span", attrs={"id": 'productTitle'}).text.strip()
    except AttributeError:
        title = ""
    return title

def get_price(soup):
    try:
        price_whole = soup.find("span", attrs={'class': 'a-price-whole'}).text.strip()
        price_fraction = soup.find("span", attrs={'class': 'a-price-fraction'}).text.strip()
        price = f"MXN ${price_whole}{price_fraction}"
    except AttributeError:
        price = "No Price Specified"
    return price

def get_rating(soup):
    try:
        rating = soup.find("span", attrs={'class': 'a-icon-alt'}).text.strip()
    except AttributeError:
        rating = "No Rating"
    return rating

def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id': 'acrCustomerReviewText'}).text.strip()
    except AttributeError:
        review_count = "No Reviews"
    return review_count

def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'}).find("span").text.strip()
    except AttributeError:
        available = "Not Available"
    return available

def fetch_url(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.read()

def is_captcha_page(soup):
    return soup.find("form", attrs={"action": "/errors/validateCaptcha"}) is not None

def save_as_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"Datos guardados en JSON: {filename}")

def save_as_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Price', 'Rating', 'Reviews', 'Availability']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Datos guardados en CSV: {filename}")

if __name__ == '__main__':
    URL = "https://www.amazon.com.mx/s?k=disco+eminem"
    HEADERS = {'User-Agent': random.choice(USER_AGENTS)}
    
    """
    1 = JSON
    2 = CSV
    3 = Both
    """    
    output_format = 3  

    try:
        webpage_content = fetch_url(URL, HEADERS)
    except urllib.error.URLError as e:
        print(f"Error al realizar la solicitud: {e}")
        exit()

    soup = BeautifulSoup(webpage_content, "html.parser")
    if is_captcha_page(soup):
        print("Se encontró un CAPTCHA. No se puede continuar.")
        exit()

    links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})
    links_list = [link.get('href') for link in links]
    data = []

    for link in links_list:
        product_url = "https://www.amazon.com.mx" + link
        HEADERS['User-Agent'] = random.choice(USER_AGENTS)

        try:
            product_content = fetch_url(product_url, HEADERS)
        except urllib.error.URLError as e:
            print(f"Error al obtener el producto: {e}")
            continue

        product_soup = BeautifulSoup(product_content, "html.parser")
        if is_captcha_page(product_soup):
            print(f"CAPTCHA detectado al intentar acceder a: {product_url}. Saltando.")
            continue

        title = get_title(product_soup)
        if title == "":
            continue
        
        product_data = {
            'Title': title,
            'Price': get_price(product_soup),
            'Rating': get_rating(product_soup),
            'Reviews': get_review_count(product_soup),
            'Availability': get_availability(product_soup)
        }

        if any(product_data.values()):
            data.append(product_data)

        delay = random.uniform(5, 15)
        print(f"Esperando {delay:.2f} segundos...")
        time.sleep(delay)

    if data:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if output_format in [1, 3]:
            json_filename = f"amazon_data_{timestamp}.json"
            save_as_json(data, json_filename)
        if output_format in [2, 3]:
            csv_filename = f"amazon_data_{timestamp}.csv"
            save_as_csv(data, csv_filename)
    else:
        print("No se encontraron datos válidos para guardar.")
