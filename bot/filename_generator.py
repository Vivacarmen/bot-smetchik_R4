# bot/filename_generator.py
"""
Центральное хранилище правил именования файлов.
ВСЕ имена файлов генерируются здесь — не менять без согласования!
"""

import re

# === ПРАВИЛА ИМЕНОВАНИЯ (не менять без одобрения CEO) ===
# Формат: [Тип]_[Клиент]_[Дата]_[Гости]_[Бренд]_ID[ID]_v[Версия].xlsx

def generate_estimate_filename(p_info, is_internal=False, version=1):
    """
    Смета (предварительная или внутренняя)
    
    Параметры:
        p_info: dict с ключами client_name, event_date, guests_qty, company, id
        is_internal: bool — внутренняя смета (с себестоимостью)
        version: int — версия документа (1, 2, 3...)
    """
    doc_type = "Внутренний_расчет" if is_internal else "Предварительная_смета"
    
    # Очистка
    client = _clean(str(p_info.get('client_name', 'Клиент')))
    date = _clean(str(p_info.get('event_date', 'Дата')))
    guests = str(p_info.get('guests_qty', '0'))
    brand = str(p_info.get('company', 'R4'))
    estimate_id = str(p_info.get('id', '00000'))
    
    filename = f"{doc_type}_{client}_{date}_{guests}г_{brand}_ID{estimate_id}_v{version}.xlsx"
    return _normalize(filename)


def generate_contract_filename(contract_info):
    """Договор"""
    number = contract_info.get('contract_number', 'I0-0000')
    client = _clean(contract_info.get('client_name', 'Клиент'))
    date = _clean(contract_info.get('contract_date', 'Дата'))
    
    return f"Договор_{number}_{client}_{date}.docx"


def generate_invoice_filename(contract_info):
    """Счёт"""
    number = contract_info.get('contract_number', 'I0-0000')
    client = _clean(contract_info.get('client_name', 'Клиент'))
    date = _clean(contract_info.get('contract_date', 'Дата'))
    
    return f"Счет_{number}_{client}_{date}.docx"


# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def _clean(text):
    """Удалить опасные символы из имени файла"""
    return re.sub(r'[^\w\s.-]', '', text).strip()

def _normalize(filename):
    """Заменить пробелы и двойные подчёркивания"""
    return filename.replace(' ', '_').replace('__', '_')
