from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_clinic_reviews(url):
    # Инициализация словаря для результатов
    result = {
        'url': url,
        "ratings": None,  # Один рейтинг (число), а не список
        "count_ratings": None,  # Количество рейтингов (число)
        "reviews": []  # Список для отзывов
    }

    # Настройка WebDriver для Firefox
    options = Options()
    options.add_argument('--headless')  # Включение headless-режима
    options.add_argument('--disable-gpu')  # Отключение GPU (для некоторых систем)
    options.add_argument('--no-sandbox')  # Это может понадобиться на некоторых системах

    service = Service('./geckodriver')
    driver = webdriver.Firefox(service=service, options=options)

    try:
        # Загрузка страницы клиники
        driver.get(url)
        print(f"Открыта страница: {driver.title}")

        # Ожидание загрузки блока с рейтингами
        ratings_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ClinicPageReviewsTags__wrapper_QX6T'))
        )

        # Парсинг страницы с помощью BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Извлечение рейтинга и количества рейтингов
        star = soup.find('div', class_='ClinicPageReviewsTags__wrapper_QX6T')
        if star:
            stat_star = star.find('span', class_='ClinicPageReviewsTags__rating-value_3sG2').text.strip().replace(',', '.')
            optz = star.find('span', class_='ClinicPageReviewsTags__reviews-count_2zvJ').text.strip()
            result['ratings'] = stat_star  
            result['count_ratings'] = optz  

        # Раскрытие отзывов путем клика на кнопку "Показать ещё" до загрузки всех отзывов
        while True:
            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="adaptive-reviews__show-more"]'))
                )
                driver.execute_script("arguments[0].click();", show_more_button)
                time.sleep(3)  # Пауза для загрузки отзывов (можно настроить)
            except Exception as e:
                print(f"Не удалось кликнуть по 'Показать ещё': {e}")
                break

        # Парсинг всех отзывов
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        reviews_section = soup.find('div', class_="AdaptiveReviews__items_KQg9")
        if reviews_section:
            reviews = reviews_section.find_all('div', class_='AdaptiveReview__root_2L8J')
            for review in reviews:
                name = review.find('span', class_='AdaptiveReviewHeader__username_35ry').text.strip()
                date = review.find('div', class_='AdaptiveReviewHeader__date_9NgC').text.strip()
                review_text = review.find('div', class_='expanding-content').text.strip()
                star = review.find('span',class_='AdaptiveReviewLabel__rating-label_YXb0').text.strip()

                result['reviews'].append({
                    'name': name,
                    'date': date,
                    'review': review_text,
                    'star': star
                })

    except Exception as e:
        print(f"Ошибка при сборе данных: {e}")

    finally:
        driver.quit()

    return result

if __name__ == "__main__":
    # Пример использования:
    url = 'https://docdoc.ru/clinic/medgorod_krylatskoe'
    result = scrape_clinic_reviews(url)
    print(result)
