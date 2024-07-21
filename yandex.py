from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

def scrape_yandex_maps_reviews(url):
    # Настройка опций для браузера Firefox
    options = Options()
    options.headless = False  # Установите True для скрытого режима
    service = Service('./geckodriver')  # Путь к geckodriver

    # Инициализация веб-драйвера
    driver = webdriver.Firefox(service=service, options=options)

    result = {
        'url': url,
        'ratings': None,
        'count_ratings': None,
        'reviews': []
    }

    try:
        # Открытие URL
        driver.get(url)
        wait = WebDriverWait(driver, 30)

        # Прокрутка страницы для загрузки большего количества отзывов
        actions = ActionChains(driver)
        for _ in range(5):  # Регулируйте количество прокруток
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1)

        # Извлечение общей оценки
        rating_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'business-summary-rating-badge-view__rating')))
        result['ratings'] = rating_element.text

        # Извлечение количества отзывов
        count_ratings_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'business-rating-amount-view')))
        result['count_ratings'] = count_ratings_element.text

        # Извлечение отзывов
        review_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "business-reviews-card-view__review")]')))
        for review_element in review_elements:
            try:
                # Извлечение имени пользователя
                name_element = review_element.find_element(By.CLASS_NAME, 'business-review-view__author-name')
                name = name_element.text.strip()
                
                # Извлечение даты отзыва
                date_element = review_element.find_element(By.CLASS_NAME, 'business-review-view__date')
                date = date_element.text.strip()
                
                # Извлечение текста отзыва
                text_element = review_element.find_element(By.CLASS_NAME, 'business-review-view__body-text')
                review_text = text_element.text.strip()
                
                # Извлечение оценки
                rating_element = review_element.find_element(By.CLASS_NAME, 'business-review-view__rating')
                rating = rating_element.get_attribute('aria-label')
                
                # Добавление отзыва в результат
                result['reviews'].append({
                    'name': name,
                    'date': date,
                    'review': review_text,
                    'star': rating
                })
            except Exception as e:
                print(f"Произошла ошибка при извлечении данных отзыва: {e}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        # Закрытие веб-драйвера
        driver.quit()

    return result

# Пример использования
if __name__ == "__main__":
    url = 'https://yandex.ru/maps/39/rostov-na-donu/?ll=39.760309%2C47.273089&mode=poi&poi%5Bpoint%5D=39.760432%2C47.271944&poi%5Buri%5D=ymapsbm1%3A%2F%2Forg%3Foid%3D1171634131&tab=reviews&z=17.26'
    result = scrape_yandex_maps_reviews(url)
    print(result)
