from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

def parse_2gis(url):
    # Настройки для Firefox
    options = Options()
    options.add_argument('--headless')  # Включение headless-режима
    options.add_argument('--disable-gpu')  # Отключение GPU (для некоторых систем)
    options.add_argument('--no-sandbox')  # Это может понадобиться на некоторых системах

    gecko_driver_path = './geckodriver'
    service = Service(gecko_driver_path)
    
    result = {
        'url': url,
        'ratings': '',
        'count_ratings': '',
        'reviews': []
    }

    try:
        # Инициализация WebDriver
        driver = webdriver.Firefox(service=service, options=options)
        # Загрузка страницы
        driver.get(url)

        # Получение HTML-кода страницы
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Извлечение общей оценки и количества отзывов
        overall_rating_elem = soup.find('div', class_='_10fd7sv')
        result['ratings'] = overall_rating_elem.text if overall_rating_elem else None
        num_reviews_elem = soup.find('div', class_='_cpls0v')
        num_reviews_text = num_reviews_elem.text.strip() if num_reviews_elem else None
        result['count_ratings'] = int(re.search(r'\d+', num_reviews_text).group()) if num_reviews_text else None

        if result['ratings'] is not None and result['count_ratings'] is not None:
            print(f"Общий рейтинг: {result['ratings']}")
            print(f"Количество отзывов: {result['count_ratings']}")
        else:
            print("Не удалось найти общий рейтинг или количество отзывов на странице.")

        # Ожидание загрузки элемента для прокрутки
        scroll_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div')))

        # Постепенная прокрутка элемента до конца
        last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_element)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_element)
            time.sleep(5)  # Задержка для загрузки новых отзывов
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_element)
            if new_height == last_height:
                break
            last_height = new_height

        time.sleep(10)  # Ожидание 10 секунд для завершения загрузки

        # Извлечение всех div с классом "_11gvyqv"
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        reviews = soup.find_all('div', class_='_11gvyqv')
        
        for review in reviews:
            # Имя пользователя
            user_name_elem = review.find('span', class_='_16s5yj36')
            user_name = user_name_elem.text.strip() if user_name_elem else "Не найдено"
            
            # Количество оценок (звездочек)
            rating_elem = review.find('div', class_='_1fkin5c')
            rating_count = len(rating_elem.find_all('span')) if rating_elem else 0
            
            # Количество оценок (звездочек)
            date_r = review.find('div', class_='_4mwq3d')
            date_r1 = date_r.text.strip()

            # Текст отзыва
            review_text_elem = review.find('a', class_='_ayej9u3')
            review_text = review_text_elem.text.strip() if review_text_elem else "Отзыв не найден"
            
            # Добавление отзыва в список
            result['reviews'].append({
                'name': user_name,
                'star': rating_count,
                'date': date_r1,
                'review': review_text
            })
            
            print(f"Имя пользователя: {user_name}")
            print(f"Дата: {date_r1}")
            print(f"Оценка: {rating_count}")
            print(f"Отзыв: {review_text}")
            print('-' * 40)

    finally:
        # Закрыть WebDriver
        driver.quit()
    
    return result

if __name__ == "__main__":
    url = 'https://2gis.ru/rostov/firm/70000001018408421/39.745337%2C47.285294/tab/reviews?m=39.740889%2C47.278096%2F15.3'
    result = parse_2gis(url)
    print(result)
