import re

class StyleConfig:
    # Цветовые схемы и официальные названия брендов
    BRAND_ASSETS = {
        'R4': {
            'color': 'E67E22',  # Оранжевый
            'display_name': 'R4 Event Design'
        },
        'Veloxy': {
            'color': '3498DB',  # Голубой
            'display_name': 'Veloxy Team'
        },
        'IM': {
            'color': '9B59B6',  # Фиолетовый
            'display_name': 'IM Production'
        },
        'default': {
            'color': '34495E',
            'display_name': 'Event Agency'
        }
    }

    @classmethod
    def get_style(cls, brand_name):
        """Возвращает настройки стиля для конкретного бренда"""
        brand_name = str(brand_name).strip()
        return cls.BRAND_ASSETS.get(brand_name, cls.BRAND_ASSETS['default'])

    @classmethod
    def generate_filename(cls, p_info, is_internal=False):
        """
        Формирует название файла по правилам:
        [Тип] смета для [Клиент]_[Дата]_[Кол-во] от [Компания].xlsx
        """
        status = "Внутренний_расчет" if is_internal else "Предварительная_смета"
        
        # Очистка данных для безопасного имени файла (удаляем спецсимволы)
        client = str(p_info.get('client_name', 'Клиент'))
        client = re.sub(r'[^\w\s.-]', '', client).strip()
        
        date = str(p_info.get('event_date', 'Дата'))
        date = re.sub(r'[^\w\s.-]', '', date).strip()
        
        guests = str(p_info.get('guests_qty', '0'))
        company = str(p_info.get('company', 'Agency'))
        
        # Собираем имя и заменяем пробелы на подчеркивания
        filename = f"{status}_для_{client}_{date}_{guests}чел_от_{company}.xlsx"
        filename = filename.replace(' ', '_')
        
        # Убираем двойные подчеркивания
        while '__' in filename:
            filename = filename.replace('__', '_')
            
        return filename
