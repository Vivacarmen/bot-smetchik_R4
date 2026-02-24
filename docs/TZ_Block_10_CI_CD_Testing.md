      Отлично, всё понял! Вот финальный **TZ_Block_10_CI_CD_Testing.md** с рекомендациями для MVP и дорожной картой на потом:

```markdown
# Блок 10: CI/CD и Тестирование

## 1. Текущее состояние и цель

| Сейчас | Цель MVP (до отъезда) | Потом (после возвращения) |
|--------|----------------------|---------------------------|
| Ручная загрузка скриптов | Git + GitHub + GitHub Actions | Docker + docker-compose |
| Тестирование вручную | Базовые тесты расчётов | Полное покрытие, CI-тесты |
| Нет мониторинга | Telegram-алерт о падении | Prometheus + Grafana |
| Production = тест | GitFlow с подсказками | Staging + production |

---

## 2. Система контроля версий (Сейчас → MVP)

### Выбор: **Git + GitHub (приватный репозиторий)**

**Почему приватный:**
- Код бота — коммерческая тайна
- Пароли в `.env` (даже если в `.gitignore`, история коммитов может утекать)
- Бесплатно для приватных репов (до 3 участников)

### Настройка (пошагово)

```bash
# 1. На VPS инициализируем Git
cd /root/projects/py
git init
git add .
git commit -m "Initial commit: MVP bot-smetchik"

# 2. Создаём приватный репозиторий на GitHub
#    Название: bot-smetchik-r4 (или ваше)
#    Settings → Private → Create

# 3. Привязываем remote
git remote add origin https://github.com/YOUR_USERNAME/bot-smetchik-r4.git
git branch -M main
git push -u origin main

# 4. Добавляем .env в .gitignore (если ещё не добавлен)
echo ".env" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "data/database.db" >> .gitignore
echo "archives/" >> .gitignore
echo "temp/" >> .gitignore
git add .gitignore
git commit -m "Add .gitignore"
git push
```

---

## 3. GitFlow с подсказками

### Схема веток

```
main          ← стабильная версия (production)
  ↑
develop       ← разработка, интеграция фич
  ↑
feature/xxx   ← конкретные задачи
  ↑
hotfix/xxx    ← срочные исправления (от main)
```

### Команды с подсказками

```bash
# === НАЧАТЬ НОВУЮ ФИЧУ ===
# 1. Переключиться на develop
git checkout develop
git pull origin develop

# 2. Создать ветку фичи
git checkout -b feature/add-expense-tracking

# 3. Работать, коммитить
git add .
git commit -m "Add expense tracking module"

# 4. Запушить на GitHub
git push -u origin feature/add-expense-tracking

# 5. Сделать Pull Request в GitHub (веб-интерфейс)
#    Compare & pull request → base: develop ← compare: feature/xxx

# === ВЛИТЬ ГОТОВУЮ ФИЧУ ===
# 6. После ревью (самостоятельно или с помощью)
git checkout develop
git pull origin develop
git merge feature/add-expense-tracking
git push origin develop

# 7. Удалить ветку фичи
git branch -d feature/add-expense-tracking
git push origin --delete feature/add-expense-tracking

# === РЕЛИЗ В PRODUCTION ===
# 8. Когда develop стабилен
git checkout main
git pull origin main
git merge develop
git tag -a v1.2.0 -m "Release v1.2.0: Expense tracking"
git push origin main --tags

# === СРОЧНЫЙ ХОТФИКС ===
# 9. Что-то сломалось в production!
git checkout main
git checkout -b hotfix/critical-bug
# ... исправляем ...
git commit -m "Fix critical bug"
git checkout main
git merge hotfix/critical-bug
git push origin main
# Потом влить в develop тоже!
git checkout develop
git merge hotfix/critical-bug
git push origin develop
```

### Подсказка в боте для CEO
```
GitFlow шпаргалка:
/feature-[название] — начать фичу
/merge-[ветка] — влить в develop
/release — влить develop в main (релиз)
/hotfix — срочный фикс

Или откройте README.md в репозитории.
```

---

## 4. CI/CD: GitHub Actions → SSH (MVP)

### Файл `.github/workflows/deploy.yml`

```yaml
name: Deploy to VPS

on:
  push:
    branches: [ main ]  # Деплой только из main

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to VPS via SSH
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.VPS_HOST }}          # IP вашего VPS
        username: ${{ secrets.VPS_USER }}      # root или botuser
        key: ${{ secrets.SSH_PRIVATE_KEY }}    # Приватный ключ SSH
        script: |
          cd /root/projects/py
          git pull origin main
          source venv/bin/activate
          pip install -r requirements.txt
          systemctl restart bot-smetchik
          echo "Deployed at $(date)" >> deploy.log
```

### Настройка Secrets в GitHub

```
Settings → Secrets and variables → Actions → New repository secret

VPS_HOST          → 123.45.67.89
VPS_USER          → root
SSH_PRIVATE_KEY   → -----BEGIN OPENSSH PRIVATE KEY-----
                    ...
                    -----END OPENSSH PRIVATE KEY-----
```

### Генерация SSH-ключа для GitHub

```bash
# На VPS
ssh-keygen -t ed25519 -C "github-actions"
# Публичный ключ (~/.ssh/id_ed25519.pub) → authorized_keys
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
# Приватный ключ (~/.ssh/id_ed25519) → в GitHub Secrets
cat ~/.ssh/id_ed25519  # Скопировать целиком в VPS_PRIVATE_KEY
```

---

## 5. Тестирование

### 5.1 Юнит-тесты (критичные модули)

**Файл `tests/test_calculations.py`:**

```python
import pytest
from bot.estimate_engine import calculate_total, apply_margin

def test_calculate_total_simple():
    services = [
        {"price": 10000, "qty": 2},
        {"price": 5000, "qty": 1}
    ]
    assert calculate_total(services) == 25000

def test_apply_margin():
    assert apply_margin(100000, 30) == 130000  # +30%

def test_tier_pricing():
    guests = 25
    tier = get_tier_price("sound", guests)  # {"1-10": 15000, "11-30": 25000}
    assert tier == 25000
```

**Запуск:**
```bash
pytest tests/ -v
```

### 5.2 Интеграционные тесты (API, БД)

```python
# tests/test_database.py
def test_expense_creation():
    db = get_db_connection()
    expense_id = create_expense(
        estimate_id=12345,
        category="CONTRACTOR",
        amount=15000
    )
    assert expense_id.startswith("EXP-")
    
    # Проверяем, что записалось
    result = db.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    assert result.fetchone() is not None
```

### 5.3 E2E тесты (Telegram-бот)

**Ручная проверка сценариев:**

| Сценарий | Шаги | Ожидаемый результат |
|----------|------|---------------------|
| Создание сметы | `/start` → пароль → `/estimate` → данные | Excel файл с правильной суммой |
| Генерация документов | Загрузить финальную смету → подтвердить | 4 файла: договор, приложение, счёт, акт |
| Внесение расхода | `/expense` → 15000 → звук → дата | Запись в БД, видна в отчёте |
| Просмотр чужой сметы | Попробовать открыть ID чужой | Доступ запрещён, алерт в лог |

### 5.4 Покрытие кода (для информации)

```bash
# Установка
pip install pytest-cov

# Запуск с покрытием
pytest --cov=bot --cov-report=html
# Отчёт в htmlcov/index.html
```

**Цель MVP:** Покрыть тестами модули:
- `estimate_engine.py` (расчёты)
- `database.py` (CRUD операции)
- `security.py` (авторизация)

**Не критично:** Telegram-хендлеры (тестируем ручно)

---

## 6. Линтер и форматтер (рекомендации)

### Для MVP: **Только `black` при коммите**

**Установка:**
```bash
pip install black
```

**Использование:**
```bash
black bot/ tests/  # Форматировать всё
```

**Pre-commit hook (опционально):**
```bash
# .git/hooks/pre-commit
#!/bin/bash
black --check bot/ || exit 1
```

**Потом добавить:**
- `flake8` (проверка стиля)
- `isort` (сортировка импортов)
- `mypy` (проверка типов)

---

## 7. Мониторинг и алерты

### Сейчас: Только логи (`logs/bot.log`)

### MVP: Telegram-алерт о падении

**Скрипт health-check:**

```bash
#!/bin/bash
# /root/health_check.sh

BOT_STATUS=$(systemctl is-active bot-smetchik)
LAST_LOG=$(tail -1 /root/projects/py/logs/bot.log | grep -c "ERROR")

if [ "$BOT_STATUS" != "active" ] || [ "$LAST_LOG" -gt 0 ]; then
    curl -s -X POST \
        "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d "chat_id=$ALERT_CHAT_ID" \
        -d "text=🚨 Бот не отвечает! Статус: $BOT_STATUS, ошибки в логе. @vivacarmen"
fi
```

**Cron:**
```bash
*/10 * * * * /root/health_check.sh
```

---

## 8. Резервное копирование кода

### Уже настроено (Блок 8): Git + Яндекс.Диск

**Дополнительно: ежедневный `git push`**

```bash
# В cron или в GitHub Actions
0 2 * * * cd /root/projects/py && git add -A && git commit -m "Auto backup $(date)" && git push
```

---

## 9. Откат версии

### Сейчас: Ручной откат через Git

```bash
# Посмотреть историю
git log --oneline -10

# Откатить на 1 коммит назад
git revert HEAD
git push origin main

# Или жёсткий откат (осторожно!)
git reset --hard HEAD~1
git push origin main --force  # ⚠️ Опасно!
```

### Потом: Docker blue-green (не для MVP)

```
Схема:
- "blue" бот: стабильная версия
- "green" бот: новая версия
- Проверяем green → переключаем nginx/webhook
- Если fail → откат к blue за 10 секунд
```

---

## 10. Документация разработчика

### Файл `README.md` (в корне)

```markdown
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

---

**ГОТОВО! 🎉**

Все 10 блоков ТЗ завершены:
1. ✅ Инфраструктура
2. ✅ User Stories
3. ✅ База знаний
4. ✅ Генерация Excel
5. ✅ Документооборот Word
6. ✅ План проекта
7. ✅ Аналитика
7.5. ✅ Учёт расходов
8. ✅ Интеграции
9. ✅ Безопасность
10. ✅ CI/CD и Тестирование

Удачной поездки и успешного запуска! ✈️
