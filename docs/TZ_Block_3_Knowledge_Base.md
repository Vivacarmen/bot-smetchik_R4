Обновлённый TZ_Block_3_Knowledge_Base.md
Markdown

Copy
Code
Preview
# Блок 3: База знаний

## 0. Технология хранения

**SQLite + SQLCipher** (шифрование всей БД)

```python
# database.py
import os
from pysqlcipher3 import dbapi2 as sqlcipher

def get_db_connection():
    conn = sqlcipher.connect(os.getenv('DB_PATH'))
    conn.execute(f"PRAGMA key = '{os.getenv('DB_ENCRYPTION_KEY')}'")
    return conn

Примечание: Все таблицы используют soft delete (is_deleted) и аудит (created_at, updated_at).

1. Таблицы смет и проектов
1.1 estimates — Сметы
Table

Copy
Поле
Тип
Описание
id
INTEGER PK
Автоинкремент
client_name
TEXT
Имя клиента
company_name
TEXT
Название компании
event_date
DATE
Дата мероприятия
guests_qty
INTEGER
Количество гостей
brand
TEXT
R4 / Veloxy / IM
total_client
INTEGER
Сумма для клиента (копейки)
total_cost
INTEGER
Себестоимость (копейки) — только CEO/Суперюзер видят
margin
INTEGER
Прибыль
margin_percent
REAL
Маржа %
status
TEXT
draft / final / contract / archived
version
INTEGER
Версия сметы (1, 2, 3...)
file_path
TEXT
Путь к Excel-файлу
created_by
INTEGER FK
Кто создал
created_at
TIMESTAMP

updated_at
TIMESTAMP
Автообновление
is_deleted
BOOLEAN
Soft delete (0/1)
1.2 estimate_items — Строки сметы
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

estimate_id
INTEGER FK

service_id
INTEGER FK
Ссылка на services
service_name
TEXT
Кэш названия (на случай изменения в справочнике)
quantity
REAL
Количество
unit_price
INTEGER
Цена за единицу
total_price
INTEGER
Итого
row_number
INTEGER
Номер строки в Excel (для связи с расходами)
created_at
TIMESTAMP

updated_at
TIMESTAMP

1.3 estimate_history — История изменений смет
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

estimate_id
INTEGER FK

client_name
TEXT
Кэш данных
company_name
TEXT

event_date
TEXT

guests_qty
INTEGER

brand
TEXT

total_client
INTEGER

total_cost
INTEGER

margin
INTEGER

margin_percent
REAL

services_used
TEXT
JSON массив ID услуг
file_path
TEXT

created_at
TIMESTAMP
Когда сохранена версия

2. Таблицы услуг и правил
2.1 services — Справочник услуг
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

name
TEXT
Название услуги
category
TEXT
Категория
unit_type
TEXT
fixed / per_team / tiered
unit_name
TEXT
Единица измерения
base_price
INTEGER
Базовая цена
cost_price
INTEGER
Себестоимость
brand
TEXT
R4 / Veloxy / IM / all
description
TEXT
Описание для AI
is_active
BOOLEAN

created_at
TIMESTAMP

updated_at
TIMESTAMP

is_deleted
BOOLEAN

2.2 service_rules — Правила расчёта
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

service_id
INTEGER FK

rule_type
TEXT
ratio / min_charge / tier / custom
rule_value
TEXT
Значение (10, 50000, или JSON)
description
TEXT

2.3 bundles — Пакеты услуг
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

name
TEXT
Название пакета
brand
TEXT
R4 / Veloxy / IM / all
description
TEXT

is_active
BOOLEAN

created_at
TIMESTAMP

updated_at
TIMESTAMP

is_deleted
BOOLEAN

2.4 bundle_items — Состав пакета
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

bundle_id
INTEGER FK

service_id
INTEGER FK

quantity
REAL

is_optional
BOOLEAN


3. Таблицы документооборота
3.1 contracts — Договоры (Блок 5)
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

estimate_id
INTEGER FK
Связь со сметой
contract_number
TEXT
I5-0325
contract_date
DATE
2025-03-15
client_inn
TEXT

client_name
TEXT
ООО "Ромашка"
client_email
TEXT
Для связи
client_phone
TEXT
Для связи
total_amount
INTEGER
Сумма договора
file_path
TEXT
Путь к файлу договора
version
INTEGER
Версия документа
created_by
INTEGER FK
Кто создал
created_at
TIMESTAMP

updated_at
TIMESTAMP

is_deleted
BOOLEAN


4. Таблицы планирования
4.1 project_tasks — Задачи проекта (Блок 6)
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

estimate_id
INTEGER FK
Связь со сметой
task_name
TEXT
Название задачи
description
TEXT
Описание (≤250 символов)
assignee
TEXT
Исполнитель (свободный ввод)
contact
TEXT
Контакт исполнителя
deadline
DATE
Дедлайн
priority
INTEGER
1-5
category
TEXT
подготовка / день_мероприятия / закрытие
depends_on
TEXT
JSON массив ID задач-предшественников, или [0]
estimate_row
INTEGER
Номер строки в смете (0 если нет)
is_flagged
BOOLEAN
⚠️ ТРЕБУЕТ ПРОВЕРКИ (AI)
created_at
TIMESTAMP

updated_at
TIMESTAMP

is_deleted
BOOLEAN


5. Таблицы учёта расходов
5.1 expenses — Фактические расходы (Блок 7.5)
Table

Copy
Поле
Тип
Описание
id
TEXT PK
EXP-ГГГГ-НННН (например, EXP-2025-0342)
estimate_id
INTEGER FK
Связь со сметой (NULL если общий)
category
TEXT
CONTRACTOR / TRANSPORT / TEAM_FOOD / MATERIALS / EMERGENCY / OVERHEAD
amount
INTEGER
Сумма в копейках
expense_date
DATE
Дата расхода
payment_method
TEXT
CASH / CARD / ACCOUNT / OTHER
payment_method_detail
TEXT
Ручной ввод для OTHER
comment
TEXT
Комментарий
created_by
INTEGER FK
Кто создал
created_at
TIMESTAMP

updated_at
TIMESTAMP

is_deleted
BOOLEAN
Soft delete
5.2 expense_history — Лог изменений расходов (Блок 7.5)
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

expense_id
TEXT FK

field_changed
TEXT
Какое поле изменено
old_value
TEXT

new_value
TEXT

changed_by
INTEGER FK
Кто изменил
changed_at
TIMESTAMP


6. Таблицы безопасности
6.1 security_logs — Лог безопасности (Блок 9)
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

timestamp
TIMESTAMP

user_id
INTEGER

user_role
TEXT

action
TEXT
login / view_estimate / edit_expense / export_analytics / ...
object_type
TEXT
estimate / expense / client_data / ...
object_id
INTEGER
ID сущности
result
TEXT
success / denied / error
ip_address
TEXT
Если доступно
details
TEXT
JSON с доп. данными
alert_sent
BOOLEAN
Был ли отправлен алерт

7. Таблицы интеграций
7.1 integration_errors — Ошибки интеграций (Блок 8)
Table

Copy
Поле
Тип
Описание
id
INTEGER PK

timestamp
TIMESTAMP

integration_name
TEXT
google_calendar / yandex_disk / telegram_log / api
event_type
TEXT
Что пытались сделать
error_message
TEXT
Текст ошибки
payload
TEXT
Данные, которые отправлялись (JSON)

8. Индексы для производительности
sql

Copy
-- Сметы по статусу и дате
CREATE INDEX idx_estimates_status ON estimates(status, created_at);

-- Расходы по проекту
CREATE INDEX idx_expenses_estimate ON expenses(estimate_id, expense_date);

-- Задачи по проекту и дедлайну
CREATE INDEX idx_tasks_estimate ON project_tasks(estimate_id, deadline);

-- Логи по пользователю и времени
CREATE INDEX idx_security_user ON security_logs(user_id, timestamp);

-- Поиск по ID расхода
CREATE INDEX idx_expense_id ON expenses(id);


9. Схема связей (ERD кратко)
plain

Copy
estimates (1)
  ├── estimate_items (N)
  ├── estimate_history (N)
  ├── contracts (0..1)
  ├── project_tasks (N)
  ├── expenses (N)
  └── [связь с users через created_by]

services (1)
  ├── service_rules (N)
  └── bundle_items (N) → bundles (N)

expenses (1) → expense_history (N)


10. Миграции (при обновлении)
При добавлении полей использовать:
Python

Copy
def migrate_add_version_to_estimates():
    conn = get_db_connection()
    try:
        conn.execute("ALTER TABLE estimates ADD COLUMN version INTEGER DEFAULT 1")
        conn.execute("UPDATE estimates SET version = 1")
        conn.commit()
    except sqlcipher.OperationalError:
        pass  # Поле уже есть


11. Резервное копирование БД
	•	Частота: Ежедневно 03:00 (локально), копия на Яндекс.Диск
	•	Формат: .tar.gz с SQLCipher-файлом (уже зашифрован)
	•	Проверка: Раз в неделю тестовое восстановление на локальной машине
