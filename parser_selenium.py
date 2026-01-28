import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
from typing import Tuple, Optional
import random


class PriceParserSelenium:
    """
    Класс для парсинга цен товаров с Ozon и Wildberries с использованием Selenium
    """
    
    def __init__(self, excel_file_path: str):
        """
        Инициализация парсера
        
        Args:
            excel_file_path: путь к Excel файлу с товарами
        """
        self.excel_file_path = excel_file_path
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Настройка Chrome драйвера"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        
        # Используем webdriver_manager для автоматической загрузки драйвера
        try:
            import undetected_chromedriver as uc
            self.driver = uc.Chrome(options=chrome_options)
        except ImportError:
            # Если не установлен undetected_chromedriver, используем стандартный
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
        
    def close_driver(self):
        """Закрытие драйвера"""
        if self.driver:
            self.driver.quit()
    
    def load_and_filter_data(self) -> pd.DataFrame:
        """
        Загрузка и фильтрация данных из Excel файла
        
        Returns:
            DataFrame с отфильтрованными товарами (цена > 1500)
        """
        print("Загрузка данных из Excel файла...")
        
        # Загружаем файл, пропуская первые 2 строки и используя 3-ю как заголовки
        df = pd.read_excel(self.excel_file_path, skiprows=2)
        
        # Переименовываем столбцы, используя первую строку как заголовки
        df.columns = df.iloc[0]
        df = df.drop(df.index[0]).reset_index(drop=True)
        
        # Преобразуем цены в числа
        df['Цена со скидкой'] = pd.to_numeric(df['Цена со скидкой'], errors='coerce')
        
        # Фильтруем товары дороже 1500 рублей
        filtered_df = df[df['Цена со скидкой'] > 1500].copy()
        
        print(f"Найдено {len(filtered_df)} товаров с ценой выше 1500 рублей")
        
        return filtered_df

    def search_ozon_price(self, article: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Поиск цены товара на Ozon по артикулу
        
        Args:
            article: артикул товара
            
        Returns:
            кортеж (цена, ссылка на товар)
        """
        if pd.isna(article) or article == '':
            return None, None
            
        try:
            print(f"Поиск на Ozon: {article}")
            
            # Открываем страницу поиска Ozon
            search_url = f"https://www.ozon.ru/search/?text={article}"
            self.driver.get(search_url)
            
            # Ждем появления результатов поиска
            try:
                # Ждем появления элементов с результатами поиска
                product_links = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/product/']"))
                )
                
                if product_links:
                    # Берем первый результат
                    product_element = product_links[0]
                    product_url = product_element.get_attribute('href')
                    
                    # Переходим на страницу товара
                    self.driver.get(product_url)
                    
                    # Ждем загрузки цены
                    try:
                        # Пытаемся найти цену на странице товара
                        price_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='price-container'], .c-subtitle-price, .display-price")
                        
                        if not price_elements:
                            # Альтернативные селекторы для цены
                            price_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ui-kit-product-price-base, .product-prices .item-price, [data-widget='pricesContainer']")
                        
                        price = None
                        for element in price_elements:
                            price_text = element.text
                            # Извлекаем числовое значение цены
                            price_match = re.search(r'[\d\s.,]+', price_text)
                            if price_match:
                                price_str = re.sub(r'[^\d.,]', '', price_match.group(0))
                                try:
                                    price = float(price_str.replace(',', '.'))
                                    break
                                except ValueError:
                                    continue
                        
                        return price, product_url
                    except TimeoutException:
                        print(f"Таймаут при поиске цены на странице товара Ozon: {article}")
                        return None, product_url
                else:
                    print(f"Не найдено результатов поиска на Ozon для артикула: {article}")
                    return None, None
                    
            except TimeoutException:
                print(f"Таймаут при поиске на Ozon для артикула: {article}")
                return None, None
                
        except Exception as e:
            print(f"Ошибка при поиске цены на Ozon для артикула {article}: {str(e)}")
            return None, None

    def search_wildberries_price(self, article: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Поиск цены товара на Wildberries по артикулу
        
        Args:
            article: артикул товара
            
        Returns:
            кортеж (цена, ссылка на товар)
        """
        if pd.isna(article) or article == '':
            return None, None
            
        try:
            print(f"Поиск на Wildberries: {article}")
            
            # Открываем страницу поиска Wildberries
            search_url = f"https://www.wildberries.ru/catalog/0/searchresult.aspx?search={article}"
            self.driver.get(search_url)
            
            # Ждем появления результатов поиска
            try:
                # Ждем появления элементов с результатами поиска
                product_cards = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-card, .goods-card"))
                )
                
                if product_cards:
                    # Берем первый результат
                    product_card = product_cards[0]
                    
                    # Находим ссылку на товар
                    link_element = product_card.find_element(By.CSS_SELECTOR, "a.product-card__link, a.j-card-link")
                    product_url = "https://www.wildberries.ru" + link_element.get_attribute('href')
                    
                    # Переходим на страницу товара
                    self.driver.get(product_url)
                    
                    # Ждем загрузки цены
                    try:
                        # Пытаемся найти цену на странице товара
                        price_elements = self.driver.find_elements(By.CSS_SELECTOR, ".price-block__final-price, .price-current, .salePrice, .j-cur-price, .price-bold")
                        
                        price = None
                        for element in price_elements:
                            price_text = element.text
                            # Извлекаем числовое значение цены
                            price_match = re.search(r'[\d\s.,]+', price_text)
                            if price_match:
                                price_str = re.sub(r'[^\d.,]', '', price_match.group(0))
                                try:
                                    price = float(price_str.replace(',', '.'))
                                    break
                                except ValueError:
                                    continue
                        
                        return price, product_url
                    except TimeoutException:
                        print(f"Таймаут при поиске цены на странице товара Wildberries: {article}")
                        return None, product_url
                else:
                    print(f"Не найдено результатов поиска на Wildberries для артикула: {article}")
                    return None, None
                    
            except TimeoutException:
                print(f"Таймаут при поиске на Wildberries для артикула: {article}")
                return None, None
                
        except Exception as e:
            print(f"Ошибка при поиске цены на Wildberries для артикула {article}: {str(e)}")
            return None, None

    def process_article(self, article: str) -> dict:
        """
        Обработка одного артикула - получение цен с обоих маркетплейсов
        
        Args:
            article: артикул товара
            
        Returns:
            словарь с результатами
        """
        print(f"Обработка артикула: {article}")
        
        # Получаем цены с обоих маркетплейсов
        ozon_price, ozon_link = self.search_ozon_price(article)
        wb_price, wb_link = self.search_wildberries_price(article)
        
        result = {
            'article': article,
            'ozon_price': ozon_price,
            'ozon_link': ozon_link,
            'wb_price': wb_price,
            'wb_link': wb_link
        }
        
        # Задержка между обработкой артикулов
        time.sleep(random.uniform(2, 5))
        
        return result

    def process_articles(self, articles: list) -> list:
        """
        Обработка списка артикулов
        
        Args:
            articles: список артикулов для обработки
            
        Returns:
            список результатов
        """
        results = []
        
        for i, article in enumerate(articles):
            print(f"Обработка артикула {i+1}/{len(articles)}: {article}")
            
            result = self.process_article(article)
            results.append(result)
        
        return results

    def save_results_to_excel(self, original_df: pd.DataFrame, results: list, output_path: str):
        """
        Сохранение результатов в Excel файл
        
        Args:
            original_df: оригинальный DataFrame
            results: результаты парсинга
            output_path: путь для сохранения результата
        """
        print("Сохранение результатов в Excel файл...")
        
        # Создаем словарь для быстрого поиска результатов по артикулу
        results_dict = {}
        for result in results:
            if result['article'] != 'ERROR':
                results_dict[result['article']] = result
        
        # Добавляем новые столбцы к оригинальному DataFrame
        original_df['Ozon Цена'] = None
        original_df['Ozon Ссылка'] = None
        original_df['Wildberries Цена'] = None
        original_df['Wildberries Ссылка'] = None
        
        # Заполняем новые столбцы данными
        for idx, row in original_df.iterrows():
            article = row['Артикул']
            if pd.notna(article) and article in results_dict:
                result = results_dict[article]
                original_df.at[idx, 'Ozon Цена'] = result['ozon_price']
                original_df.at[idx, 'Ozon Ссылка'] = result['ozon_link']
                original_df.at[idx, 'Wildberries Цена'] = result['wb_price']
                original_df.at[idx, 'Wildberries Ссылка'] = result['wb_link']
        
        # Сохраняем в Excel
        original_df.to_excel(output_path, index=False)
        print(f"Результаты сохранены в файл: {output_path}")


def main():
    """
    Основная функция
    """
    # Путь к исходному файлу
    input_file = '/workspace/Прайс_Ingco+WadFow.xlsx'
    output_file = '/workspace/Результат_парсинга_цен_selenium.xlsx'
    
    # Создаем экземпляр парсера
    parser = PriceParserSelenium(input_file)
    
    try:
        # Настройка драйвера
        parser.setup_driver()
        
        # Загружаем и фильтруем данные
        df = parser.load_and_filter_data()
        
        # Получаем список артикулов для обработки (берем только первые 3 для тестирования)
        articles = df['Артикул'].dropna().tolist()  # Убираем пустые значения
        test_articles = articles[:3]  # Берем только 3 для теста
        print(f"Всего артикулов для обработки: {len(articles)}, тестовых: {len(test_articles)}")
        
        # Обрабатываем артикулы
        results = parser.process_articles(test_articles)
        
        # Сохраняем результаты
        parser.save_results_to_excel(df, results, output_file)
        
        print("Обработка завершена!")
        print("\nРезультаты:")
        for result in results:
            print(f"Артикул: {result['article']}")
            print(f"  Ozon цена: {result['ozon_price']}, ссылка: {result['ozon_link']}")
            print(f"  WB цена: {result['wb_price']}, ссылка: {result['wb_link']}")
            print()
        
    except Exception as e:
        print(f"Ошибка при выполнении: {str(e)}")
    finally:
        # Закрываем драйвер
        parser.close_driver()


if __name__ == "__main__":
    main()