from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def get_google_maps_reviews(url):
    """
    Извлекает отзывы с заданной страницы Google Maps.
    
    Args:
        url (str): URL страницы с отзывами на Google Maps.

    Returns:
        dict: Словарь с данными об отзывах.
    """
    result = {
        'url': url,
        'ratings': '',
        'count_ratings': '',
        'reviews': []
    }

    options = Options()
    options.add_argument('--headless')  # Включение headless-режима
    options.add_argument('--disable-gpu')  # Отключение GPU (для некоторых систем)
    options.add_argument('--no-sandbox')  # Это может понадобиться на некоторых системах

    service = Service('./geckodriver')
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get(url)

        # Ожидание загрузки элемента с отзывами
        element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde"))
        )

        # Прокрутка до конца списка отзывов
        last_height = driver.execute_script("return arguments[0].scrollHeight", element)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
            time.sleep(2)
            new_height = driver.execute_script("return arguments[0].scrollHeight", element)
            if new_height == last_height:
                break
            last_height = new_height

        # Парсинг страницы
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Извлечение общей оценки
        rating_element = soup.find(class_="fontDisplayLarge")
        if rating_element:
            result['ratings'] = rating_element.text.strip()

        # Извлечение количества отзывов
        count_element = soup.find("div", class_="F7nice")
        if count_element:
            result['count_ratings'] = count_element.text.strip().split()[0]

        # Извлечение отзывов
        reviews = soup.find_all(class_="jftiEf fontBodyMedium")
        for review in reviews:
            review_data = {}
            
            # Имя пользователя
            name_element = review.find(class_="d4r55")
            if name_element:
                review_data['name'] = name_element.text.strip()
             # Дата    
            data = review.find(class_='rsqaWe')
            if data:
                review_data['date'] = data.text.strip()

            # Оценка пользователя
            rating_element = review.find(class_="DU9Pgb")
            if rating_element:
                rating = rating_element.find(attrs={"aria-label": True})
                if rating:
                    review_data['star'] = rating['aria-label'].split()[0]

            # Текст отзыва
            text_element = review.find(class_="wiI7pd")
            if text_element:
                review_data['review'] = text_element.text.strip()

            if review_data:
                result['reviews'].append(review_data)

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        driver.quit()

    return result
if __name__ == "__main__":
    # Пример использования
    url = "https://www.google.com/maps/place/%D0%A1%D0%BF%D0%BE%D1%80%D1%82%D0%B8%D0%B2%D0%BD%D1%8B%D0%B9+%D0%9A%D0%BB%D1%83%D0%B1+%D0%90%D1%80%D0%BC%D0%B8%D0%B8+%D0%A1%D0%BA%D0%B2%D0%BE,+%D0%A1%D1%82%D0%B0%D0%B4%D0%B8%D0%BE%D0%BD/@47.2717004,39.7145185,15z/data=!4m18!1m9!3m8!1s0x40e3b8308d77d6b3:0x520e930845014fed!2z0JDQqNCQ0J0!8m2!3d47.258333!4d39.722638!9m1!1b1!16s%2Fg%2F1pzt7h5hm!3m7!1s0x40e3b9a8f82b0a17:0xace90ce312ef9703!8m2!3d47.2716113!4d39.7277222!9m1!1b1!16zL20vMGIwbHJn?entry=ttu"
    result = get_google_maps_reviews(url)
    print(result)