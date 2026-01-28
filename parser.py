import pandas as pd
import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup
import time
from typing import Dict, List, Tuple, Optional
import random
import json


class PriceParser:
    """
    Класс для парсинга цен товаров с Ozon и Wildberries
    """
    
    def __init__(self, excel_file_path: str):
        """
        Инициализация парсера
        
        Args:
            excel_file_path: путь к Excel файлу с товарами
        """
        self.excel_file_path = excel_file_path
        self.session = None
        
    async def __aenter__(self):
        """Контекстный менеджер для сессии aiohttp"""
        # Настройка сессии с обходом защиты
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=2)
        timeout = aiohttp.ClientTimeout(total=30)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста"""
        if self.session:
            await self.session.close()

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

    async def search_ozon_price(self, article: str) -> Tuple[Optional[float], Optional[str]]:
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
            # Добавим случайную задержку для обхода защиты
            await asyncio.sleep(random.uniform(1, 3))
            
            # Пытаемся найти товар по артикулу на Ozon
            search_url = f"https://www.ozon.ru/search/?text={article}"
            
            # Обновляем User-Agent для каждого запроса
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.ozon.ru/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Cache-Control': 'max-age=0',
            }
            
            async with self.session.get(search_url, headers=headers) as response:
                if response.status != 200:
                    print(f"Ошибка при запросе к Ozon для артикула {article}: статус {response.status}")
                    return None, None
                    
                html = await response.text()
                
                # Ищем ссылку на товар в HTML
                # Сначала пробуем найти через JSON-LD данные или специальные дата-атрибуты
                product_url_match = re.search(r'"(https://www\.ozon\.ru/product/[^"]+)"', html)
                if not product_url_match:
                    # Альтернативный паттерн
                    product_url_match = re.search(r'href="(https://www\.ozon\.ru/product/[^"]+)"', html)
                
                if product_url_match:
                    product_url = product_url_match.group(1)
                    
                    # Проверим страницу товара для получения точной цены
                    try:
                        async with self.session.get(product_url, headers=headers) as product_response:
                            if product_response.status == 200:
                                product_html = await product_response.text()
                                
                                # Ищем цену на странице продукта
                                # Паттерн для поиска цены в формате JSON или скриптах
                                price_patterns = [
                                    r'"originalPrice":\s*(\d+)',
                                    r'"priceValue":\s*"([\d.,]+)"',
                                    r'"price":\s*(\d+)',
                                    r'<meta property="product:price:amount"[^>]*content="(\d+)"',
                                    r'"(?:recommendedPrice|price)":\s*\{[^}]*?"value":\s*(\d+)',
                                    r'"price-data"[^>]*data-price="(\d+)"'
                                ]
                                
                                for pattern in price_patterns:
                                    price_match = re.search(pattern, product_html)
                                    if price_match:
                                        try:
                                            price = float(price_match.group(1))
                                            return price, product_url
                                        except ValueError:
                                            continue
                                
                                # Если не нашли в JSON, ищем в HTML
                                soup = BeautifulSoup(product_html, 'lxml')
                                
                                # Ищем элементы с ценой
                                price_selectors = [
                                    '[data-testid="price-container"]',
                                    '.c-subtitle-price',
                                    '.product-prices .item-price',
                                    '[data-widget="pricesContainer"]',
                                    '.display-price'
                                ]
                                
                                for selector in price_selectors:
                                    price_element = soup.select_one(selector)
                                    if price_element:
                                        price_text = price_element.get_text(strip=True)
                                        price_match = re.search(r'[\d\s.,]+', price_text)
                                        if price_match:
                                            price_str = re.sub(r'[^\d.,]', '', price_match.group(0))
                                            try:
                                                price = float(price_str.replace(',', '.'))
                                                return price, product_url
                                            except ValueError:
                                                continue
                                
                                # Если все равно не нашли цену, возвращаем URL без цены
                                return None, product_url
                    except Exception as e:
                        print(f"Ошибка при получении страницы товара на Ozon: {str(e)}")
                        # Все равно возвращаем найденный URL
                        return None, product_url
                
                print(f"Не удалось найти товар на Ozon по артикулу: {article}")
                return None, None
                
        except Exception as e:
            print(f"Ошибка при поиске цены на Ozon для артикула {article}: {str(e)}")
            return None, None

    async def search_wildberries_price(self, article: str) -> Tuple[Optional[float], Optional[str]]:
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
            # Добавим случайную задержку для обхода защиты
            await asyncio.sleep(random.uniform(1, 3))
            
            # Wildberries API для поиска по артикулу
            # Сначала попробуем использовать API поиска
            search_url = f"https://search.wb.ru/exactmatch/v2/header/q/{article}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.wildberries.ru/',
            }
            
            # Попробуем получить информацию через API
            async with self.session.get(search_url, headers=headers) as response:
                if response.status != 200:
                    print(f"API Wildberries недоступен для артикула {article}, пробуем альтернативный метод")
                    return await self._wildberries_fallback_search(article)
                    
                data = await response.json()
                
                # Если нашли товар через API
                if 'data' in data and 'products' in data['data'] and data['data']['products']:
                    product = data['data']['products'][0]
                    product_id = product.get('id')
                    
                    if product_id:
                        # Получаем детали товара
                        product_url = f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx"
                        
                        # Цены могут быть в разных форматах
                        price = None
                        if 'salePriceU' in product:
                            price = product['salePriceU'] / 100  # цена в копейках
                        elif 'priceU' in product:
                            price = product['priceU'] / 100  # цена в копейках
                        elif 'prices' in product:
                            prices = product['prices']
                            if 'salePrice' in prices:
                                price = prices['salePrice']
                        
                        return price, product_url
                
                return await self._wildberries_fallback_search(article)
                
        except Exception as e:
            print(f"Ошибка при поиске цены на Wildberries для артикула {article}: {str(e)}")
            # Возвращаемся к обычному поиску
            return await self._wildberries_fallback_search(article)

    async def _wildberries_fallback_search(self, article: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Резервный метод поиска на Wildberries
        
        Args:
            article: артикул товара
            
        Returns:
            кортеж (цена, ссылка на товар)
        """
        try:
            search_url = f"https://www.wildberries.ru/catalog/0/searchresult.aspx?search={article}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.wildberries.ru/',
            }
            
            # Добавим случайную задержку
            await asyncio.sleep(random.uniform(1, 3))
            
            async with self.session.get(search_url, headers=headers) as response:
                if response.status != 200:
                    print(f"Ошибка при запросе к Wildberries для артикула {article}: статус {response.status}")
                    return None, None
                    
                html = await response.text()
                
                # Ищем ссылку на товар в HTML
                # Попробуем найти ID товара из JSON или data-атрибутов
                product_id_match = re.search(r'"productId":\s*(\d+)', html)
                if not product_id_match:
                    product_id_match = re.search(r'data-product-id="(\d+)"', html)
                
                if product_id_match:
                    product_id = product_id_match.group(1)
                    product_url = f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx"
                    
                    # Попробуем получить данные о товаре отдельным запросом к API
                    api_url = f"https://card.wb.ru/cards/detail?nm={product_id}"
                    async with self.session.get(api_url, headers=headers) as api_response:
                        if api_response.status == 200:
                            api_data = await api_response.json()
                            
                            # Ищем цену в API ответе
                            if 'data' in api_data and 'products' in api_data['data'] and api_data['data']['products']:
                                product_info = api_data['data']['products'][0]
                                
                                price = None
                                if 'salePriceU' in product_info:
                                    price = product_info['salePriceU'] / 100
                                elif 'priceU' in product_info:
                                    price = product_info['priceU'] / 100
                                elif 'prices' in product_info:
                                    prices = product_info['prices']
                                    if 'salePrice' in prices:
                                        price = prices['salePrice']
                                
                                return price, product_url
                
                # Если не нашли через API, ищем в HTML
                soup = BeautifulSoup(html, 'lxml')
                
                # Ищем товары на странице
                products = soup.find_all('div', class_='product-card')
                
                if products:
                    product = products[0]
                    
                    # Ищем ссылку на товар
                    link_element = product.find('a', class_=re.compile(r'product-card__link|j-card-link'))
                    if link_element and 'href' in link_element.attrs:
                        product_url = 'https://www.wildberries.ru' + link_element['href']
                        
                        # Ищем цену
                        price_element = product.find('span', class_=re.compile(r'price|cost', re.I))
                        if not price_element:
                            price_element = product.find('ins', class_=re.compile(r'price', re.I))
                        if not price_element:
                            price_element = product.find('span', class_=re.compile(r'j-cur-price|salePrice|price-bold'))
                            
                        if price_element:
                            price_text = price_element.get_text(strip=True)
                            # Извлекаем числовое значение цены
                            price_match = re.search(r'[\d\s.,]+', price_text.replace(' ', ''))
                            if price_match:
                                price_str = re.sub(r'[^\d.,]', '', price_match.group(0))
                                try:
                                    price = float(price_str.replace(',', '.'))
                                    return price, product_url
                                except ValueError:
                                    pass
                
                print(f"Не удалось найти товар на Wildberries по артикулу: {article}")
                return None, None
                
        except Exception as e:
            print(f"Ошибка при резервном поиске на Wildberries для артикула {article}: {str(e)}")
            return None, None

    async def process_article(self, article: str) -> Dict[str, any]:
        """
        Обработка одного артикула - получение цен с обоих маркетплейсов
        
        Args:
            article: артикул товара
            
        Returns:
            словарь с результатами
        """
        print(f"Обработка артикула: {article}")
        
        # Получаем цены с обоих маркетплейсов
        ozon_task = self.search_ozon_price(article)
        wb_task = self.search_wildberries_price(article)
        
        ozon_price, ozon_link = await ozon_task
        wb_price, wb_link = await wb_task
        
        return {
            'article': article,
            'ozon_price': ozon_price,
            'ozon_link': ozon_link,
            'wb_price': wb_price,
            'wb_link': wb_link
        }

    async def process_articles_batch(self, articles: List[str], batch_size: int = 3) -> List[Dict[str, any]]:
        """
        Обработка списка артикулов с ограничением одновременных запросов
        
        Args:
            articles: список артикулов для обработки
            batch_size: количество одновременных запросов
            
        Returns:
            список результатов
        """
        results = []
        
        # Разбиваем на батчи для избежания блокировки
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            print(f"Обработка батча {i//batch_size + 1}/{(len(articles)-1)//batch_size + 1}")
            
            # Создаем задачи для текущего батча
            valid_articles = [article for article in batch if pd.notna(article) and article != '']
            if not valid_articles:
                continue
                
            tasks = [self.process_article(article) for article in valid_articles]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обрабатываем результаты
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    print(f"Ошибка при обработке артикула {valid_articles[j]}: {result}")
                    # Добавляем пустой результат в случае ошибки
                    results.append({
                        'article': valid_articles[j],
                        'ozon_price': None,
                        'ozon_link': None,
                        'wb_price': None,
                        'wb_link': None
                    })
                else:
                    results.append(result)
            
            # Задержка между батчами для избежания блокировки
            if i + batch_size < len(articles):
                await asyncio.sleep(random.uniform(3, 5))  # Увеличиваем задержку
        
        return results

    def save_results_to_excel(self, original_df: pd.DataFrame, results: List[Dict[str, any]], output_path: str):
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


async def main():
    """
    Основная функция
    """
    # Путь к исходному файлу
    input_file = '/workspace/Прайс_Ingco+WadFow.xlsx'
    output_file = '/workspace/Результат_парсинга_цен.xlsx'
    
    # Создаем экземпляр парсера
    async with PriceParser(input_file) as parser:
        # Загружаем и фильтруем данные
        df = parser.load_and_filter_data()
        
        # Получаем список артикулов для обработки (берем только первые 5 для тестирования)
        articles = df['Артикул'].dropna().tolist()  # Убираем пустые значения
        print(f"Всего артикулов для обработки: {len(articles)}")
        
        # Обрабатываем артикулы (берем только первые 5 для тестирования)
        test_articles = articles[:5]
        print(f"Тестовая обработка артикулов: {test_articles}")
        results = await parser.process_articles_batch(test_articles)
        
        # Сохраняем результаты
        parser.save_results_to_excel(df, results, output_file)
        
        print("Тестовая обработка завершена!")
        print("\nРезультаты:")
        for result in results:
            print(f"Артикул: {result['article']}")
            print(f"  Ozon цена: {result['ozon_price']}, ссылка: {result['ozon_link']}")
            print(f"  WB цена: {result['wb_price']}, ссылка: {result['wb_link']}")
            print()


if __name__ == "__main__":
    asyncio.run(main())