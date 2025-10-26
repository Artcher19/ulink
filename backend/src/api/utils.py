import os

async def calculate_control_digit(link_id: int) -> int:
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

async def delete_current_db_files(database_path: str):
    db_path = database_path
    db_dir = os.path.dirname(db_path)
    db_name = os.path.basename(db_path)
    db_name_without_ext = os.path.splitext(db_name)[0]

    files_to_remove = [
        db_path,
        os.path.join(db_dir, db_name_without_ext + "-wal"),
        os.path.join(db_dir, db_name_without_ext + "-shm"),
        os.path.join(db_dir, db_name_without_ext + "-journal")
        ]
        
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    