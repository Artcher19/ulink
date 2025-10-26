import asyncio
from httpx import ASGITransport, AsyncClient
import pytest
from api.utils import calculate_control_digit
from main import app


@pytest.mark.asyncio()
async def test_calculate_control_digit():
    assert await calculate_control_digit(12345) == 7 #проверка из примера
    assert await calculate_control_digit(71) == 0 #проверка с остатком 0 на шаге 4
    assert await calculate_control_digit(13011) == 0 #проверка с остатком 0 на шаге 4

@pytest.mark.asyncio(loop_scope="session")
async def test_root():
    injection_tests = [
            # 1. Классическая UNION-based инъекция
            "98080' UNION SELECT 1,2,3,4--",
            
            # 2. Инъекция с комментарием для обхода проверок
            "98080' OR '1'='1'--",
            
            # 3. Инъекция с подзапросом
            "98080' AND (SELECT COUNT(*) FROM links) > 0--",
            
            # 4. Инъекция для получения информации о БД
            "98080' AND 1=CAST((SELECT version()) AS int)--",
            
            # 5. Инъекция для обхода аутентификации
            "98080' OR link_id IS NOT NULL--",
            
            # 6. Инъекция с множественными условиями
            "98080'; DROP TABLE links--",
            
            # 7. Инъекция для получения данных других таблиц
            "98080' UNION SELECT link_id, full_link, short_link, create_date FROM links--",
            
            # 8. Инъекция с подстановкой всегда истинного условия
            "98080' OR 'x'='x",
            
            # 9. Инъекция для проверки на ошибки
            "98080' AND 1=1--",
            
            # 10. Инъекция с кавычками разных типов
            '98080" OR "1"="1',
            
            # 11. Инъекция для проверки порядка колонок
            "98080' ORDER BY 1--",
            "98080' ORDER BY 4--",
            
            # 12. URL-encoded инъекции
            "98080%27%20OR%20%271%27%3D%271",
            "98080%22%20OR%20%221%22%3D%221",
        ]
     
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        for injection in injection_tests:
            response = await ac.get(f"/{injection}")
            # Ожидаем либо 404 (не найдено), либо 300 (редирект), но не 500 (ошибка сервера)
            assert response.status_code in [300, 404, 422], f"Injection {injection} caused unexpected status: {response.status_code}"
    

@pytest.mark.asyncio(loop_scope="session")
async def test_redirect_user_edge_cases():    
    # Граничные случаи и специальные символы (только валидные для URL)
    edge_cases = [
        # Пустая строка
        "",
        # Только специальные символы
        "'",
        '"',
        # SQL ключевые слова
        "SELECT",
        "DROP",
        "UNION",
        # Очень длинная строка (но валидные символы)
        "A" * 500,
        # Unicode символы (валидные в URL)
        "%D1%82%D0%B5%D1%81%D1%82",  # "тест" в URL encoding
        "%F0%9F%8E%AF",  # "🎯" в URL encoding
        # Пробелы (заменяем на + или %20)
        "98080%20",
        "+98080+",
        # Комбинации
        "98080' OR '1",
        # Числовые инъекции
        "0",
        "-1",
        "999999999",
        # Специальные символы в URL encoding
        # "%00",  # NULL байт
        "%0A",  # новая строка
        "%0D",  # возврат каретки
    ]
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        for case in edge_cases:
            response = await ac.get(f"/{case}")
            # Ожидаем корректную обработку (не 500 ошибку)
            assert response.status_code != 500, f"Edge case {repr(case)} caused server error"


@pytest.mark.asyncio(loop_scope="session")
async def test_redirect_user_valid_cases():    
    # Тесты с валидными ссылками для проверки нормальной работы
    valid_cases = [
        "98080",
        "12345",
        "10000",
        "99999",
    ]
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        for case in valid_cases:
            response = await ac.get(f"/{case}")
            # Для существующих ссылок ожидаем 300, для несуществующих - 404
            assert response.status_code in [300, 404], f"Valid case {case} caused unexpected status: {response.status_code}"

@pytest.mark.asyncio(loop_scope="session")
async def test_paraller_post_requests():    
    # Количество параллельных запросов
    num_requests = 100
    
    async def create_link(client, index):
        """Вспомогательная функция для создания ссылки с уникальным URL"""
        data = {"full_link": f"https://example.com/page{index}"}
        response = await client.post("/links", json=data)
        return response
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Создаем несколько параллельных запросов
        tasks = [create_link(ac, i) for i in range(num_requests)]
        responses = await asyncio.gather(*tasks)
        
        # Проверяем, что все запросы завершились успешно
        successful_responses = 0
        short_links = []
        
        for i, response in enumerate(responses):
            if response.status_code == 200:
                successful_responses += 1
                data = response.json()
                short_link = data["short_link"]
                # Извлекаем только числовую часть (без домена)
                numeric_part = short_link.split("/")[-1]
                short_links.append(numeric_part)
                print(f"Request {i}: Success - {short_link}")
            else:
                print(f"Request {i}: Failed with status {response.status_code}")
        
        # Проверяем основные утверждения
        assert successful_responses == num_requests, f"Expected {num_requests} successful requests, got {successful_responses}"
        
        # Проверяем, что все ссылки уникальны
        assert len(short_links) == len(set(short_links)), f"Duplicate short links found: {short_links}"
        
        # Проверяем, что все ссылки имеют правильный формат
        for link in short_links:
            assert link.isdigit(), f"Short link {link} is not numeric"
            # Проверяем контрольную цифру
            base_number = int(link[:-1])  # Все кроме последней цифры
            control_digit = int(link[-1])  # Последняя цифра
            expected_control = await calculate_control_digit(base_number)
            assert control_digit == expected_control, f"Control digit mismatch for {link}"
        
        print(f"✓ Successfully created {num_requests} unique short links in parallel")

@pytest.mark.asyncio(loop_scope="session")
async def test_parallel_redirect_requests():
    # Ссылки для тестирования редиректа
    test_links = ["100014",
                   "100021", 
                   "100038", 
                   "100045", 
                   "100052",
                   "100076",
                   "100090"]
    
    async def perform_redirect(client, link):
        """Вспомогательная функция для выполнения редиректа"""
        response = await client.get(link)
        return response
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Создаем несколько параллельных запросов редиректа
        tasks = [perform_redirect(ac, link) for link in test_links]
        responses = await asyncio.gather(*tasks)
        
        # Проверяем, что все запросы завершились успешно
        successful_redirects = 0
        redirect_statuses = []
        
        for i, response in enumerate(responses):
            # Для существующих ссылок ожидаем статус 307 (Temporary Redirect) или 308 (Permanent Redirect)
            if response.status_code in [307, 308]:
                successful_redirects += 1
                redirect_url = response.headers.get("location", "No location header")
                redirect_statuses.append({
                    "link": test_links[i],
                    "status": response.status_code,
                    "location": redirect_url
                })
                print(f"Redirect {i}: Success - {test_links[i]} -> {redirect_url} (Status: {response.status_code})")
            else:
                print(f"Redirect {i}: Failed for {test_links[i]} with status {response.status_code}")
        
        # Проверяем основные утверждения
        assert successful_redirects == len(test_links), f"Expected {len(test_links)} successful redirects, got {successful_redirects}"
        
        # Проверяем, что все редиректы ведут на валидные URL
        for status_info in redirect_statuses:
            assert status_info["location"].startswith(("http://", "https://")), f"Invalid redirect location: {status_info['location']}"
        
        print(f"✓ Successfully processed {len(test_links)} parallel redirect requests")
