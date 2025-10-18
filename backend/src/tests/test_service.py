from httpx import ASGITransport, AsyncClient
import pytest
import aiohttp
from api.service import calculate_control_digit
from api.links import redirect_user
from fastapi.testclient import TestClient
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
            assert response.status_code in [300, 404], f"Injection {injection} caused unexpected status: {response.status_code}"
    

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
        "%00",  # NULL байт
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