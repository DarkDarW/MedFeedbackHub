from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape1_reviews(url):
    # Настройка опций Firefox
    options = Options()
    options.add_argument('--headless')  # Включение headless-режима
    options.add_argument('--disable-gpu')  # Отключение GPU (для некоторых систем)
    options.add_argument('--no-sandbox')  # Это может понадобиться на некоторых системах


    # Добавление пользовательского заголовка
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, как Gecko) Chrome/58.0.3029.110 Safari/537.3'
    options.set_preference('general.useragent.override', user_agent)

    # Маскировка Selenium
    options.set_preference('dom.webdriver.enabled', False)
    options.set_preference('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Дополнительные заголовки для имитации реального браузера
    options.set_preference('network.http.sendRefererHeader', 2)
    options.set_preference('network.http.referer.spoofSource', False)
    options.set_preference('privacy.trackingprotection.enabled', False)

    # Путь к geckodriver
    service = Service('./geckodriver')  # Замените на правильный путь

    # Создание экземпляра Firefox
    driver = webdriver.Firefox(service=service, options=options)

    # Открытие сайта
    driver.get(url)

    # Случайное время ожидания для имитации поведения пользователя
    time.sleep(random.uniform(10, 20))

    # Структура для хранения результата
    result = {
        'url': url,
        'ratings': None,
        'count_ratings': None,
        'reviews': []
    }

    try:
        # Ожидание загрузки рейтинга и количества отзывов
        rating_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'rating'))
        )
        review_count_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'router-link-active.router-link-exact-active.doctorReview'))
        )
        
        # Извлечение рейтинга и количества отзывов
        result['ratings'] = rating_element.text
        result['count_ratings'] = int(review_count_element.text.split()[0])
        
        print(f"Рейтинг: {result['ratings']}")
        print(f"Количество отзывов: {result['count_ratings']}")

        page_number = 1
        while True:
            # Ожидание загрузки отзывов на текущей странице
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'review-teaser.full'))
            )

            # Сбор отзывов на текущей странице
            reviews = driver.find_elements(By.CLASS_NAME, 'review-teaser.full')
            for review in reviews:
                try:
                    name = review.find_element(By.CLASS_NAME, 'review-teaser__name').text
                    rating = review.find_element(By.CLASS_NAME, 'rating').text
                    description = review.find_element(By.CLASS_NAME, 'review-teaser__desc').text
                    star = review.find_element(By.CLASS_NAME, 'rating').text
                    date = review.find_element(By.CLASS_NAME, 'review-teaser__date').text
                    result['reviews'].append({
                        'name': name,
                        'rating': rating,
                        'review': description,
                        'star' : star,
                        'date': date
                    })
                except Exception as e:
                    print(f"Произошла ошибка при сборе данных отзыва: {e}")

            # Переход на следующую страницу
            try:
                next_page_xpath = f"//*[@id='num-{page_number}']"
                next_page = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, next_page_xpath))
                )
                next_page.click()
                page_number += 1

                # Ожидание загрузки следующей страницы
                time.sleep(random.uniform(5, 10))
            except Exception as e:
                print(f"Достигнута последняя страница с отзывами. Ошибка при переходе на страницу {page_number}: {e}")
                break

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    # Закрытие Firefox
    driver.quit()

    # Вывод общего количества отзывов
    total_reviews = len(result['reviews'])
    print(f"Общее количество отзывов: {total_reviews}")

    # Вывод собранных отзывов (опционально)
    for i, review in enumerate(result['reviews'], 1):
        print(f"Отзыв {i}:")
        print(f"Имя: {review['name']}")
        print(f"Оценка: {review['rating']}")
        print(f"Дата: {review['date']}")
        print(f"Отзыв: {review['review']}\n")
    
    return result

if __name__ == "__main__":
    url = 'https://doctu.ru/msk/clinic/visus-novus/reviews'
    result = scrape1_reviews(url)
    print(result)