import re

def extract_project_details(text):
    """
    Автоматически ищет в тексте параметры для шапки Excel.
    Поддерживает сложные форматы дат и диапазоны времени.
    """
    details = {
        "client_name": "Клиент",
        "event_date": "Дата не указана",
        "guests_qty": "0"
    }
    
    # 1. Поиск ВРЕМЕНИ (например, 16:00, 16:00-18:00, с 10:00 до 19:00)
    # Ищем паттерны с двоеточием, поддерживая диапазоны через дефис или тире
    time_match = re.search(r'(\d{1,2}:\d{2}(?:\s*[-–]\s*\d{1,2}:\d{2})?)', text)
    event_time = time_match.group(0).strip() if time_match else ""

    # 2. Поиск ДАТЫ
    # Поддерживает разделители: . / - и текстовые названия месяцев
    date_pattern = r'(\d{1,2}(?:[-–]\d{1,2})?[\.\/\s]+(?:[а-яА-Яa-zA-Z]+|\d{2})(?:[\.\/\s]+\d{2,4})?)'
    date_match = re.search(date_pattern, text)
    
    if date_match:
        extracted_date = date_match.group(0).strip()
        # Если время найдено, объединяем их в одну строку для шапки
        if event_time:
            details["event_date"] = f"{extracted_date} ({event_time})"
        else:
            details["event_date"] = extracted_date
    elif event_time:
        # Если найдено только время без даты
        details["event_date"] = f"Дата не указана ({event_time})"
    
    # 3. Поиск количества гостей (число + ключевое слово)
    people_match = re.search(r'(\d+)\s*(чел|гост|человек|персон|участ)', text, re.I)
    if people_match: 
        details["guests_qty"] = people_match.group(1)
    
    # 4. Поиск КЛИЕНТА
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        first_line = lines[0]
        # Если первая строка короткая, считаем её именем клиента или названием проекта
        if len(first_line) < 50:
            clean_name = re.sub(r'^(Клиент|Заказчик|Проект)[:\s-]*', '', first_line, flags=re.I)
            details["client_name"] = clean_name.strip()
        
    return details

def get_safe_filename(p_info, is_internal=False):
    """Генерирует безопасное имя файла без спецсимволов для ОС"""
    status = "Внутр_расчет" if is_internal else "Предв_смета"
    
    # Очищаем дату и время от символов, запрещенных в именах файлов (:, /, пробелы)
    raw_date = p_info.get('event_date', 'Дата')
    safe_date = re.sub(r'[:\(\)\/\s]', '_', raw_date)
    
    # Очищаем имя клиента
    client_name = p_info.get('client_name', 'Клиент')
    safe_client = re.sub(r'[^\w\s.-]', '', client_name).strip().replace(' ', '_')
    
    guests = p_info.get('guests_qty', '0')
    
    return f"{status}_для_{safe_client}_{safe_date}_{guests}чел.xlsx"
