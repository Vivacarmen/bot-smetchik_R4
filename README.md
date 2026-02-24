# Bot-Smetchik R4

Телеграм-бот для автоматизации смет event-компании R4.

## Быстрый старт

```bash
# 1. Клонировать
git clone https://github.com/YOUR_USERNAME/bot-smetchik-r4.git 
cd bot-smetchik-r4

# 2. Создать .env (см. .env.example)
cp .env.example .env
# Редактировать: nano .env

# 3. Установить зависимости
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Инициализировать БД
python -m bot.database init

# 5. Запустить
python -m bot.main
```

## Структура проекта

```
bot/
  __init__.py
  main.py              # Точка входа
  config.py            # Конфигурация
  handlers.py          # Telegram-хендлеры
  database.py          # Работа с БД
  estimate_engine.py   # Расчёты смет
  ...
```

## Команды GitFlow

См. раздел 3 в документации.

## Тестирование

```bash
pytest tests/ -v
```

## Деплой

Автоматический при push в `main` через GitHub Actions.
```

---

## 11. Чек-лист перед релизом (v1.0 MVP)

| Проверка | Как | Ответственный |
|----------|-----|---------------|
| Расчёт сметы = Excel | Создать 3 сметы, сравнить цифры | Менеджер |
| Генерация документов | Открыть Word, проверить все `{{поля}}` | CEO |
| Telegram-команды | Пройти все сценарии из Блока 2 | Менеджер |
| Безопасность (пароли) | Попробовать войти с wrong password ×5 | Админ |
| Бэкап работает | Проверить файл на Яндекс.Диске | Админ |
| Логи пишутся | Найти запись о своём действии в `security_logs` | Админ |
| Git push/pull | Проверить синхронизацию с GitHub | Разработчик |
| Health-check | Остановить бот, проверить алерт в Telegram | Админ |

---

## 12. Дорожная карта (после возвращения)

| Этап | Что делаем | Срок |
|------|-----------|------|
| v1.1 | Docker + docker-compose, staging бот | 2 недели |
| v1.2 | Полное покрытие тестами (80%+) | 2 недели |
| v1.3 | Prometheus + Grafana мониторинг | 1 неделя |
| v1.4 | Blue-green деплой, zero-downtime | 1 неделя |
| v2.0 | API для мобильного приложения | 3 недели |

