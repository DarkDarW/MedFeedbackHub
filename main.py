from prodoctorov import parse_prodoctorov
from gis import parse_2gis
from yandex import scrape_yandex_maps_reviews
from doc1 import scrape_clinic_reviews
from doctu import scrape1_reviews
from napopravky import scrape_re
from google import get_google_maps_reviews

def scrape_yandex_maps_reviews_func(url):
    return scrape_yandex_maps_reviews(url)

def scrape_re_func(url):
    return scrape_re(url)

def scrape_reviews_func(url):
    return scrape1_reviews(url)

def parse_prodoctorov_func(url):
    return parse_prodoctorov(url)

def parse_2gis_func(url):
    return parse_2gis(url)

def scrape_clinic_reviews_func(url):
    return scrape_clinic_reviews(url)

def get_google_maps_reviews_func(url):
    return get_google_maps_reviews(url)

def parse(platform, url):
    if platform == 'prodoctorov':
        return parse_prodoctorov_func(url)
    elif platform == 'napopravku':
        return scrape_re_func(url)
    elif platform == 'yandex':
        return scrape_yandex_maps_reviews_func(url)
    elif platform == '2gis':
        return parse_2gis_func(url)
    elif platform == 'docturu':
        return scrape_reviews_func(url)
    elif platform == 'sberzdrav':
        return scrape_clinic_reviews_func(url)  
    elif platform == 'googlemaps':
        return get_google_maps_reviews_func(url)
    else:
        return {'error': 'Скоро добавим'}

if __name__ == "__main__":
    platform = 'napopravku'  # Измените на 'prodoctorov' для тестирования другой платформы
    url = 'www.gis'
    
    result = parse(platform, url)
    print(result)
