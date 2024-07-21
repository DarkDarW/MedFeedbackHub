from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

def parse_prodoctorov(url):
    result = {
        'url': url,
        'rating': None,
        'count_ratings': None,
        'reviews': []
    }

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    service = Service('./geckodriver')
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'b-reviews-page')))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract overall rating
        rating_element = soup.find('div', class_='b-stars-rate__progress')
        if rating_element:
            style_attr = rating_element.get('style', '')
            width_value = re.search(r'width:\s*([\d.]+)em', style_attr)
            if width_value:
                width_em = float(width_value.group(1))
                rating = round(width_em, 1) - 1
                result['rating'] = rating

        # Extract count of ratings
        count_ratings_elem = soup.find('span', class_='b-box-rating__text')
        if count_ratings_elem:
            result['count_ratings'] = count_ratings_elem.get_text(strip=True)

        # Extract reviews
        review_elements = soup.find_all('div', class_='b-review-card year2024 b-review-card_positive')
        for review_elem in review_elements:
            try:
                author = review_elem.find('div', class_='b-review-card__author-link').text.strip()
                date = review_elem.find('div', class_='ui-text ui-text_body-2 ui-kit-color-text-secondary mb-5').text.strip()
                rating = review_elem.find('span', class_='ui-text ui-text_subtitle-2 ui-kit-color-text ml-1').text.strip()
                text = review_elem.find('div', class_='b-review-card__comment ui-text ui-text_body-1 ui-kit-color-text mt-2').text.strip()

                review = {
                    'name': author,
                    'date': date,
                    'star': rating,
                    'review': text
                }

                result['reviews'].append(review)

            except AttributeError as e:
                print(f"Ошибка при извлечении отзыва: {str(e)}")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        result = None

    finally:
        driver.quit()

    return result

if __name__ == '__main__':
    url = "https://prodoctorov.ru/rostov-na-donu/lpu/45713-medicinskiy-centr-semya-na-budennovskom-prospekte/otzivi/#tab-content"
    result = parse_prodoctorov(url)
    if result:
        print(result)
