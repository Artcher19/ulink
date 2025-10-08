from sqlalchemy import func, select
from api.dependencies import SessionDep
from models.links import LinkModel


async def calculate_control_digit(link_id: int):
    """
    Вычисляет контрольный разряд для сокращенной части ссылки.
    
    Args:
        link_id (int): Сокращенная часть динамической ссылки (цифры)
    
    Returns:
        int: Контрольный разряд (0-9)
    """
    # Преобразуем число в строку цифр
    digits_str = str(link_id)
    
    # Нумерация справа налево (реверсируем)
    reversed_digits = digits_str[::-1]
    
    # Подсчет сумм четных и нечетных позиций
    even_sum = 0
    odd_sum = 0
    
    for i, digit_char in enumerate(reversed_digits, start=1):
        digit = int(digit_char)
        if i % 2 == 0:  # четные позиции
            even_sum += digit
        else:  # нечетные позиции
            odd_sum += digit
    
    # Общая сумма = сумма_четных + 3 * сумма_нечетных
    total_sum = even_sum + 3 * odd_sum
    
    # Вычисление контрольного разряда
    remainder = total_sum % 10
    return 0 if remainder == 0 else 10 - remainder

async def get_next_link_id(session: SessionDep) -> int:
    """Получить следующий ID для ссылки, начиная с 10000"""
    result = await session.execute(select(func.max(LinkModel.link_id)))
    max_id = result.scalar()
    
    if max_id is None:
        return 10000
    else:
        return max_id + 1