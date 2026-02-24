     Понял, исправляю! Вот обновлённый **TZ_Block_8_Integrations.md** с правками:

```markdown
# Блок 8: Интеграции

## 1. Общие принципы

- **Конфигурация:** Отдельный файл `integrations.yaml`
- **Аутентификация API:** API-ключ в заголовке `X-API-Key`
- **Уведомления:** Webhook при событиях
- **Логирование:** Только ошибки интеграций (изменено согласно уточнению)
- **Документация:** `README.md` с примерами запросов (изменено согласно уточнению)
- **MVP (сейчас):** Telegram-лог, Google Calendar, Яндекс.Диск
- **Потом:** Полный API для мобильного приложения

## 2. Интеграция: Telegram (лог запросов)

### Назначение
Отдельный чат для фиксации входящих запросов от клиентов.

### Данные в сообщении
```
📥 Новый запрос от клиента

👤 Контакт: Иванов Иван, +7 (999) 123-45-67
💬 Telegram: @ivanov_client
🆔 ID проекта: 12345
📋 Название: Тимбилдинг Ромашка
👨‍💼 Создатель: @petrov_manager
⏰ Время запроса: 25.03.2025 14:32
```

### Конфигурация (`integrations.yaml`)
```yaml
telegram_log:
  enabled: true
  chat_id: "-1001234567890"  # ID чата для логов
  events:
    - new_estimate_request    # Новая смета запрошена
    - client_contact_shared   # Клиент поделился контактом
    - document_package_ready  # Комплект документов готов
```

### Реализация
- Отправка через Bot API (тот же токен, другой chat_id)
- Асинхронно, не блокирует основной поток
- При ошибке — запись в `error.log`, повторная попытка не требуется

---

## 3. Интеграция: Google Calendar

### 3.1 Даты мероприятий

**Событие создаётся при:** финализации сметы (статус "договор")

**Содержимое события:**
```
Название: [ID12345] Тимбилдинг Ромашка
Описание: 
  Проект: Тимбилдинг для ООО "Ромашка"
  ID сметы: 12345
  Создатель: @petrov_manager
  Клиент: Иванов Иван, +7 (999) 123-45-67, @ivanov_client
  Сумма: 169 889 ₽
  Ссылка на смету: https://bot.example.com/estimates/12345

Дата/время: 25.03.2025 10:00 - 25.03.2025 18:00 (из сметы)
Календарь: Общий календарь компании (R4 Events)
Участники: petrov_manager@company.com (если email известен)
```

### 3.2 Дедлайны задач из плана проекта

**Событие создаётся при:** генерации плана проекта (Блок 6)

**Содержимое события:**
```
Название: [Задача #15] Заказ звука — Тимбилдинг Ромашка
Описание:
  Проект: Тимбилдинг Ромашка (ID 12345)
  Задача: Заказ звука
  Исполнитель: (не назначен)
  Приоритет: 4/5
  Категория: подготовка
  Срок: за 3 дня до мероприятия

Дата: 22.03.2025 (весь день)
Календарь: Общий календарь компании
Цвет: 🔴 Красный (если приоритет 5), 🟡 Жёлтый (приоритет 3-4), 🟢 Зелёный (1-2)
```

### Конфигурация (`integrations.yaml`)
```yaml
google_calendar:
  enabled: true
  service_account_file: "/root/projects/py/config/google_service_account.json"
  calendar_id: "r4events@group.calendar.google.com"
  sync:
    events: true           # Мероприятия
    tasks: true            # Дедлайны задач
  reminder_minutes: [1440, 60]  # За сутки и за час
```

### Реализация
- Google Calendar API (v3)
- Service Account (не OAuth пользователя)
- При ошибке — запись в `error.log`, событие не создаётся (ручная повторная синхронизация по запросу)

---

## 4. Интеграция: Яндекс.Диск (бэкап)

### Что бэкапим
- База данных (`data/database.db`)
- Логи (`logs/`)
- Архивы смет и документов (`archives/`)
- Временные файлы (`temp/` — перед очисткой)
- Конфиги (`integrations.yaml`, `.env` — шифрованно)

### Структура на Яндекс.Диске
```
/backup/
  /2025/
    /03/
      /25/
        backup_2025-03-25_03-00.tar.gz      # Ежедневный
        backup_2025-03-25_15-30.tar.gz      # Дополнительный (по запросу)
    /weekly/
      backup_week_11_2025.tar.gz             # Еженедельный (понедельник)
    /monthly/
      backup_month_03_2025.tar.gz            # Ежемесячный (1-е число)
```

### Конфигурация (`integrations.yaml`)
```yaml
yandex_disk:
  enabled: true
  oauth_token: "${YANDEX_DISK_TOKEN}"  # Из .env
  backup_path: "/backup/"
  schedule:
    daily: "03:00"        # Ежедневно в 3:00
    weekly: "Monday"    # По понедельникам
    monthly: "1"          # 1-го числа
  retention:
    daily: 7             # Хранить 7 дневных
    weekly: 4            # Хранить 4 недельных
    monthly: 12          # Хранить 12 месячных
  include:
    - data/
    - logs/
    - archives/
    - config/integrations.yaml
  exclude:
    - temp/*              # Кроме явно помеченных
    - *.pyc
    - __pycache__/
```

### Реализация
- Yandex Disk REST API (webdav)
- Скрипт `backup_yandex.sh` + cron (или Python-scheduler)
- Шифрование архива паролем (опционально, ключ в `.env`)

---

## 5. API для будущего мобильного приложения

### Эндпоинты (заготовка)

| Метод | Эндпоинт | Описание | Статус |
|-------|----------|----------|--------|
| GET | `/api/v1/estimates` | Список смет (с фильтрами) | 🟡 Заготовка |
| GET | `/api/v1/estimates/{id}` | Детали сметы | 🟡 Заготовка |
| POST | `/api/v1/estimates` | Создать смету | 🔴 Потом |
| PUT | `/api/v1/estimates/{id}` | Обновить смету | 🔴 Потом |
| GET | `/api/v1/clients` | Список клиентов | 🟡 Заготовка |
| GET | `/api/v1/clients/{id}` | Детали клиента | 🟡 Заготовка |
| GET | `/api/v1/expenses` | Расходы по проекту | 🟡 Заготовка |
| POST | `/api/v1/expenses` | Добавить расход | 🔴 Потом |
| GET | `/api/v1/analytics/summary` | Сводная аналитика | 🟡 Заготовка |
| GET | `/api/v1/tasks` | Задачи проекта | 🟡 Заготовка |
| POST | `/api/v1/webhooks/subscribe` | Подписка на webhook | 🟡 Заготовка |

### Аутентификация
```
Headers:
  X-API-Key: sk_live_abc123xyz789
  Content-Type: application/json
```

### Webhook-события (заготовка)
```json
{
  "event": "estimate.finalized",
  "timestamp": "2025-03-25T14:32:00Z",
  "data": {
    "estimate_id": 12345,
    "client_name": "ООО Ромашка",
    "total_amount": 169889,
    "manager_id": 42
  }
}
```

### Конфигурация (`integrations.yaml`)
```yaml
api:
  enabled: false          # Пока отключено, заготовка для потом
  version: "v1"
  auth:
    type: "api_key"
    header: "X-API-Key"
    keys:                 # Из .env или БД
      - "${API_KEY_MOBILE}"
  rate_limit:
    requests_per_minute: 60
  webhooks:
    enabled: true
    retry_attempts: 3
    retry_delay_seconds: 5
```

---

## 6. Структура integrations.yaml

```yaml
# integrations.yaml — конфигурация внешних интеграций

telegram_log:
  enabled: true
  chat_id: "-1001234567890"
  events:
    - new_estimate_request
    - client_contact_shared
    - document_package_ready

google_calendar:
  enabled: true
  service_account_file: "/root/projects/py/config/google_service_account.json"
  calendar_id: "r4events@group.calendar.google.com"
  sync:
    events: true
    tasks: true
  reminder_minutes: [1440, 60]

yandex_disk:
  enabled: true
  oauth_token: "${YANDEX_DISK_TOKEN}"
  backup_path: "/backup/"
  schedule:
    daily: "03:00"
    weekly: "Monday"
    monthly: "1"
  retention:
    daily: 7
    weekly: 4
    monthly: 12

api:
  enabled: false
  version: "v1"
  auth:
    type: "api_key"
    header: "X-API-Key"
  rate_limit:
    requests_per_minute: 60
  webhooks:
    enabled: true
    retry_attempts: 3
    retry_delay_seconds: 5
```

---

## 7. Обработка ошибок

| Интеграция | При ошибке | Логирование |
|------------|-----------|-------------|
| Telegram-лог | Игнорировать | `error.log` |
| Google Calendar | Пропустить, ручная синхронизация позже | `error.log` |
| Яндекс.Диск | Повторить через 1 час (3 попытки) | `error.log` |
| API (когда включим) | 500 + retry webhook | `error.log` |

---

## 8. Документация для разработчиков

### README.md
Файл `README.md` в корне проекта с разделом **Integrations**:

```markdown
## Интеграции

### Telegram Log
```bash
# Тест отправки лога
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"event":"test","chat_id":"-1001234567890"}' \
  http://localhost:8000/test/telegram
```

### Google Calendar
```bash
# Ручная синхронизация
python -m bot.scripts.sync_calendar --estimate-id=12345
```

### API (заготовка)
```bash
# Получить список смет
curl -X GET \
  -H "X-API-Key: sk_live_abc123xyz789" \
  http://localhost:8000/api/v1/estimates

# Webhook подписка
curl -X POST \
  -H "X-API-Key: sk_live_abc123xyz789" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://mobile.example.com/webhook","events":["estimate.finalized"]}' \
  http://localhost:8000/api/v1/webhooks/subscribe
```
```

---

## 9. Что НЕ реализуется (в MVP)

| Интеграция | Причина | Когда |
|------------|---------|-------|
| CRM (Битрикс24, amoCRM) | Нет CRM в компании | При внедрении CRM |
| 1С / бухгалтерия | Нет 1С в облаке | При переходе на 1С Online |
| Email-отправка клиенту | Нет SMTP, сложно | Блок 11 (потом) |
| Slack / WhatsApp | Не требуется | — |
| Телефония | Нет CallTouch/Ringostat | — |
| Полная документация API (Swagger) | Нет необходимости в MVP | При открытии API |
| Postman-коллекция | Нет необходимости в MVP | При открытии API |

---

## 10. Таблица БД для интеграций

```sql
-- Лог ошибок интеграций (только ошибки!)
CREATE TABLE integration_errors (
    id INTEGER PRIMARY KEY,
    integration_name TEXT,      -- 'google_calendar', 'yandex_disk', etc.
    event_type TEXT,            -- что пытались сделать
    error_message TEXT,         -- текст ошибки
    payload TEXT,               -- данные, которые отправлялись
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 11. Команды для ручной синхронизации

| Команда | Доступ | Описание |
|---------|--------|----------|
| `/sync_calendar` | Админ+ | Принудительная синхронизация с Google Calendar |
| `/sync_yandex` | Админ+ | Принудительный бэкап на Яндекс.Диск |
| `/test_webhook` | Суперюзер | Тестовый webhook-запрос |
| `/api_status` | Админ+ | Статус API (включено/выключено, количество ключей) |

---

**Готов для сохранения!**

Следующий блок — **Блок 9: Безопасность**?
