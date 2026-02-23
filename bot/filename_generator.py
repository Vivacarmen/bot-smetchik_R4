import re

def generate_filename(p_info, is_internal=False, version=1):
    doc_type = "Внутренний_расчет" if is_internal else "Предварительная_смета"
    client = re.sub(r'[^\w\s.-]', '', str(p_info.get('client_name', 'Клиент'))).strip()
    date = re.sub(r'[^\w\s.-]', '', str(p_info.get('event_date', 'Дата'))).strip()
    guests = str(p_info.get('guests_qty', '0'))
    brand = str(p_info.get('company', 'R4'))
    estimate_id = str(p_info.get('id', '00000'))
    
    filename = f"{doc_type}_{client}_{date}_{guests}г_{brand}_ID{estimate_id}_v{version}.xlsx"
    return filename.replace(' ', '_').replace('__', '_')
