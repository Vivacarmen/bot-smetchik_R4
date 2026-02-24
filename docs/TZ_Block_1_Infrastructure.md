Обновлённый TZ_Block_1_Infrastructure.md
Markdown

Copy
Code
Preview
# Блок 1: Инфраструктура

## 1. Требования к серверу

| Параметр | Значение |
|----------|----------|
| CPU | 1 Core |
| RAM | 1GB (для LLM через API) / 8GB (для локальной LLM) |
| Диск | 20GB SSD |
| ОС | Ubuntu 22.04 LTS |
| Локация | РФ (для скорости Telegram) |

## 2. Структура проекта

/root/projects/py/
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py                 # ← Обновлён (6 паролей + Gemini)
│   ├── handlers.py
│   ├── ai_proxy.py              # ← Нужно починить Gemini
│   ├── estimate_engine.py        # ← Поменять импорт filename
│   ├── filename_generator.py    # ← НОВЫЙ ФАЙЛ (здесь!)
│   ├── header_builder.py
│   ├── style_config.py          # ← Оставляем, но убираем generate_filename
│   ├── utils.py
│   ├── prompts.py
│   ├── database.py
│   └── analytics.py
├── config/                       # ← НОВОЕ: конфиги интеграций
│   ├── integrations.yaml         # Настройки внешних сервисов
│   └── google_service_account.json # Google Calendar API
├── data/
│   ├── database.db               # SQLCipher-шифрованная БД
│   ├── knowledge/                # База знаний AI
│   └── templates/                # Шаблоны Word/Excel
├── archives/                     # Структурированный архив
│   ├── contracts/                # ← НОВОЕ: договоры по годам
│   │   └── 2025/
│   ├── expenses/                 # ← НОВОЕ: чеки, сканы расходов
│   │   └── 2025/
│   └── backups/                  # ← НОВОЕ: резервные копии БД
│       ├── daily/
│       ├── weekly/
│       └── monthly/
├── logs/
│   ├── bot.log                   # Основной лог
│   ├── errors.log                # Ошибки
│   ├── access.log                # Доступы (кто что смотрел)
│   └── security.log              # ← НОВОЕ: security_events (Блок 9)
├── temp/                         # Временные файлы (очистка через 7 дней)
├── .env                          # Переменные окружения
├── requirements.txt              # Зависимости Python
├── README.md                     # Документация разработчика
└── scripts/                      # ← НОВОЕ: служебные скрипты
    ├── backup_bot.sh             # Ежедневный бэкап
    ├── backup_yandex.sh          # Бэкап на Яндекс.Диск
    └── health_check.sh           # ← НОВОЕ: проверка работы бота

## 3. Переменные окружения (.env)

```bash
# API-ключи
GROQ_API_KEY=gsk_...
TELEGRAM_TOKEN=6371359479:AAH...

# Безопасность: пароли ролей
ACCESS_PASSWORD_CLIENT=client2025
ACCESS_PASSWORD_AGENT=agent2025
ACCESS_PASSWORD_MANAGER=manager2025
ACCESS_PASSWORD_ADMIN=admin2025
ACCESS_PASSWORD_CEO=ceo2025
ACCESS_PASSWORD_SUPERUSER=superuser2025

# Безопасность: шифрование БД
DB_ENCRYPTION_KEY=YourStrongPassword123!  # ← НОВОЕ: SQLCipher

# Интеграции
TELEGRAM_LOG_CHAT_ID=-1001234567890       # ← НОВОЕ: чат для логов
YANDEX_DISK_TOKEN=y0_AgAAAA...
API_KEY_MOBILE=sk_live_abc123xyz789       # ← НОВОЕ: заготовка API

# Пути
DB_PATH=/root/projects/py/data/database.db
ARCHIVE_PATH=/root/projects/py/archives
TEMP_PATH=/root/projects/py/temp
LOG_PATH=/root/projects/py/logs
CONFIG_PATH=/root/projects/py/config        # ← НОВОЕ

# Настройки
CLEANUP_DAYS=7                  # Очистка temp
ARCHIVE_QUARTER=true            # Архивация по кварталам
USE_PROXY=false                 # Xray/VLESS если нужен

4. Зависимости (requirements.txt)
plain

Copy
# Основа
python-telegram-bot==20.7
aiogram==3.4.1

# База данных
pysqlcipher3==1.2.0             # ← НОВОЕ: SQLCipher для шифрования

# AI
groq==0.4.2
openai==1.12.0

# Excel/Word
openpyxl==3.1.2
python-docx==0.8.11

# Интеграции
google-api-python-client==2.120.0
google-auth-httplib2==0.2.0
yadisk==1.3.3                   # Яндекс.Диск

# Утилиты
python-dotenv==1.0.0
requests==2.31.0
Pillow==10.2.0

# Тестирование (Блок 10)
pytest==8.0.2
pytest-cov==4.1.0
black==24.2.0                   # Форматирование

5. Резервное копирование
5.1 Локальный бэкап (ежедневно 03:00)
bash

Copy
#!/bin/bash
# /root/projects/py/scripts/backup_bot.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/root/projects/py/archives/backups/daily"
mkdir -p $BACKUP_DIR

# SQLCipher: резерв копируется как есть (уже шифрован)
tar -czf $BACKUP_DIR/bot_backup_$DATE.tar.gz \
  /root/projects/py/data/ \
  /root/projects/py/config/ \
  /root/projects/py/logs/

# Ротация: хранить 7 дней
find $BACKUP_DIR -name "bot_backup_*.tar.gz" -mtime +7 -delete

# Копия на Яндекс.Диск (через отдельный скрипт)
/root/projects/py/scripts/backup_yandex.sh $BACKUP_DIR/bot_backup_$DATE.tar.gz

5.2 Яндекс.Диск (Блок 8)
	•	Weekly: archives/backups/weekly/
	•	Monthly: archives/backups/monthly/
	•	Retention: 4 недели, 12 месяцев
5.3 Git + GitHub (Блок 10)
	•	Ежедневный git push в 02:00
	•	Приватный репозиторий
	•	Автодеплой из main через GitHub Actions
6. Мониторинг и health-check
6.1 Проверка работы бота
bash

Copy
#!/bin/bash
# /root/projects/py/scripts/health_check.sh

BOT_STATUS=$(systemctl is-active bot-smetchik)
LAST_ERROR=$(tail -100 /root/projects/py/logs/errors.log | grep -c "$(date +%Y-%m-%d)" || echo "0")

if [ "$BOT_STATUS" != "active" ] || [ "$LAST_ERROR" -gt 10 ]; then
    curl -s -X POST \
        "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_LOG_CHAT_ID" \
        -d "text=🚨 ALERT: Бот-smetchik не отвечает! Статус: $BOT_STATUS, ошибок сегодня: $LAST_ERROR. @vivacarmen"
fi

Cron:
bash

Copy
*/10 * * * * /root/projects/py/scripts/health_check.sh

6.2 Очистка temp
bash

Copy
# Ежедневно в 04:00
0 4 * * * find /root/projects/py/temp/ -type f -mtime +7 -delete

7. Docker (заготовка для потом)
dockerfile

Copy
# Dockerfile (не используется в MVP)
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bot/ ./bot/
COPY config/ ./config/
COPY data/ ./data/

ENV DB_ENCRYPTION_KEY=${DB_ENCRYPTION_KEY}
CMD ["python", "-m", "bot.main"]

Примечание: Docker не используется в MVP (Блок 1, п.7 оригинала). Оставлено как заготовка.
8. Webhook vs Polling
MVP: Polling (реализация в main.py)
Webhook — потом:
	•	Требуется домен + SSL
	•	Endpoint: https://pu.r4project.ru/webhook
	•	Настройка в integrations.yaml (Блок 8)
9. Чек-лист деплоя
	•	[ ] .env создан, все ключи заполнены
	•	[ ] config/ создан, integrations.yaml заполнен
	•	[ ] SQLCipher: DB_ENCRYPTION_KEY ≠ дефолтный
	•	[ ] Права на папки: chmod 700 data/ archives/ logs/
	•	[ ] Git инициализирован, приватный репозиторий на GitHub
	•	[ ] Cron настроен: backup, health_check, cleanup
	•	[ ] Тестовый запуск: python -m bot.main
