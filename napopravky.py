# Убедитесь, что у вас установлены все необходимые библиотеки
from httpcore import TimeoutException
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_re(url):
    options = Options()
    options.add_argument('--headless')  # Включение headless-режима
    options.add_argument('--disable-gpu')  # Отключение GPU (для некоторых систем)
    options.add_argument('--no-sandbox')  # Это может понадобиться на некоторых системах

    service = Service('./geckodriver')  # Update with your actual path to geckodriver
    driver = webdriver.Firefox(service=service, options=options)

    result = {
        'url': url,
        'ratings': [],
        'count_ratings': '',
        'reviews': []
    }

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        rating_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rating-overview__value')))
        rating = rating_element.text.strip()

        reviews_count_element = driver.find_element(By.CLASS_NAME, 'text-sm.text-dark-gray')
        reviews_count = reviews_count_element.text.strip()

        result['ratings'].append(rating)
        result['count_ratings'] = reviews_count

        print(f"Общая оценка: {rating}")
        print(f"Количество отзывов: {reviews_count}")

        page_number = 1
        while True:
            page_url = url + f'page-{page_number}/'
            print(f"\nПарсинг страницы {page_number}: {page_url}")
            driver.get(page_url)

            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'review-list__review-container')))
            except TimeoutException:
                print(f"Не удалось загрузить отзывы на странице {page_url}")
                break

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            reviews = soup.find_all('div', class_='review-list__review-container')
            if not reviews:
                print(f"На странице {page_url} нет отзывов.")
                break

            for review in reviews:
                try:
                    author = review.find('div', class_='photo-block__text-title').text.strip()
                    rating = review.find('div', class_='n-rating__wrp').text.strip()
                    text = review.find('div', class_='review__content-wrapper').text.strip()

                    result['reviews'].append({
                        'name': author,
                        'star': rating,
                        'review': text
                    })

                    print(f"Автор: {author}\nОценка: {rating}\nОтзыв: {text}\n---")
                except AttributeError:
                    print("Не удалось извлечь данные из отзыва")

            page_number += 1
            time.sleep(2)  # Add delay between requests

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    finally:
        driver.quit()

    return result

if __name__ == '__main__':
    url = 'https://napopravku.ru/moskva/clinics/medtsentrservis-na-sokole/otzyvy/'
    result = scrape_re(url)
    print(result)
