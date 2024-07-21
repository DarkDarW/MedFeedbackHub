from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def parse_prodoctorov(url):
    options = Options()
    options.headless = True
    service = Service('./geckodriver')
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'opinion-item')))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        reviews = []
        review_elements = soup.find_all('div', class_='opinion-item')
        for review_elem in review_elements:
            try:
                author = review_elem.find('span', class_='opinion-author').text.strip()
                date = review_elem.find('span', class_='opinion-date').text.strip()
                rating = review_elem.find('span', class_='opinion-rate').text.strip()
                text = review_elem.find('div', class_='opinion-text').text.strip()

                review = {
                    'author': author,
                    'date': date,
                    'rating': rating,
                    'text': text
                }

                reviews.append(review)

            except AttributeError as e:
                print(f"Ошибка при извлечении отзыва: {str(e)}")

        # Сбор информации о рейтингах
        ratings = []
        count_ratings = None
        rating_elements = soup.find_all('span', class_='opinion-rate')
        for rating_elem in rating_elements:
            try:
                rating = rating_elem.text.strip()
                ratings.append(rating)
            except AttributeError:
                continue

        try:
            count_ratings_elem = soup.find('div', class_='widget-title')
            if count_ratings_elem:
                count_ratings = int(count_ratings_elem.text.split(' ')[0])
        except AttributeError:
            pass

        return {
            'url': url,
            'ratings': ratings,
            'count_ratings': count_ratings,
            'reviews': reviews
        }

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return None

    finally:
        driver.quit()

if __name__ == '__main__':
    url = "https://prodoctorov.ru/rostov-na-donu/lpu/45713-medicinskiy-centr-semya-na-budennovskom-prospekte/otzivi/#tab-content"
    result = parse_prodoctorov(url)
    
    if result:
        print(f"URL: {result['url']}")
        print(f"Количество рейтингов: {result['count_ratings']}")
        print("Рейтинги:")
        for rating in result['ratings']:
            print(f"- {rating}")
        print("Отзывы:")
        for review in result['reviews']:
            print(f"Автор: {review['author']}")
            print(f"Дата: {review['date']}")
            print(f"Рейтинг: {review['rating']}")
            print(f"Отзыв: {review['text']}")
            print("---")
