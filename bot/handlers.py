import logging
import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

# Импорты из пакета bot
from bot import config
from bot import prompts
from bot.ai_proxy import AIClient
from bot.estimate_engine import EstimateBuilder
from bot.utils import extract_project_details, get_safe_filename

# Константы состояний диалога
AUTH, MENU, SELECT_COMPANY, CLIENT_DETAILS, COMPANY_NAME, LOCATION, PROJECT_PARAMS, TRAINING = range(8)

# Инициализация сервисов (прокси включается через USE_PROXY в .env)
ai_client = AIClient(use_proxy=getattr(config, 'USE_PROXY', False))
estimate_builder = EstimateBuilder()

# --- РАБОТА С БАЗОЙ ДАННЫХ (SQLite) ---

def init_db():
    """Инициализация таблицы знаний в БД."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge (id INTEGER PRIMARY KEY, content TEXT)''')
    conn.commit()
    conn.close()

def save_knowledge(text):
    """Сохранение нового прайса или инструкции в БД."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO knowledge (content) VALUES (?)", (text,))
    conn.commit()
    conn.close()

def get_pricing_knowledge():
    """Извлечение всех накопленных знаний для передачи в промпт."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM knowledge")
    rows = cursor.fetchall()
    conn.close()
    return "\n---\n".join([row[0] for row in rows]) if rows else "Используй стандартные рыночные цены."

# --- ОБРАБОТЧИКИ АВТОРИЗАЦИИ И МЕНЮ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало работы и проверка авторизации."""
    if context.user_data.get('auth_done'): 
        return await show_main_menu(update, context)
    await update.message.reply_text("🔐 Система формирования смет.\nВведите пароль для доступа:")
    return AUTH

async def handle_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка пароля."""
    if update.message.text == config.ACCESS_PASSWORD:
        context.user_data['auth_done'] = True
        return await show_main_menu(update, context)
    await update.message.reply_text("❌ Пароль неверный. Попробуйте еще раз:")
    return AUTH

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение главного меню."""
    keyboard = [["🚀 Создать смету"], ["📚 Обучить бота", "⚙️ Настройки"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("📊 ГЛАВНОЕ МЕНЮ:\nВыберите действие:", reply_markup=reply_markup)
    return MENU

# --- ЛОГИКА СОЗДАНИЯ СМЕТЫ ---

async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "🚀 Создать смету" or choice == "1":
        keyboard = [["R4", "Veloxy"], ["IM", "Отмена"]]
        await update.message.reply_text(
            "Выберите бренд для сметы:", 
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return SELECT_COMPANY
    elif choice == "📚 Обучить бота" or choice == "2":
        await update.message.reply_text(
            "Отправьте текст с ценами или инструкциями. Я запомню их.", 
            reply_markup=ReplyKeyboardRemove()
        )
        return TRAINING
    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.")
        return await show_main_menu(update, context)

async def select_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "Отмена": 
        return await show_main_menu(update, context)
    
    context.user_data['company'] = choice
    await update.message.reply_text(f"Выбран бренд: {choice}\n\nВведите имя контактного лица (клиента):", reply_markup=ReplyKeyboardRemove())
    return CLIENT_DETAILS

async def get_client_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['client_person'] = update.message.text
    await update.message.reply_text("Введите название компании заказчика:")
    return COMPANY_NAME

async def get_company_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['client_org'] = update.message.text
    await update.message.reply_text("Укажите локацию (площадку):")
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['location'] = update.message.text
    await update.message.reply_text("Опишите задачу (дата, время, кол-во гостей, программа):")
    return PROJECT_PARAMS

async def handle_project_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Основной процесс генерации через ИИ."""
    user_text = update.message.text
    await update.message.reply_text("⏳ Генерирую сметы... Это может занять около минуты.")
    
    training_data = get_pricing_knowledge()
    company = context.user_data.get('company', 'Agency')
    prompt = prompts.get_estimate_prompt(company, user_text, training_data)
    
    try:
        response = await ai_client.ask(prompt)
    except Exception as e:
        logging.error(f"Критическая ошибка AI API: {e}")
        response = None
    
    if not response:
        error_info = "Не удалось получить ответ от ИИ."
        log_path = os.path.join(config.LOG_PATH, "ai_error_log.txt")
        
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    error_info += f"\n🔍 Причина: {lines[-1].strip()}"
                else:
                    error_info += "\n🔍 Причина: Ошибка соединения с API."
        else:
            error_info += "\n🔍 Причина: Сервис AI недоступен."
        
        await update.message.reply_text(f"❌ {error_info}")
        return await show_main_menu(update, context)

    try:
        project_info = extract_project_details(user_text)
        project_info.update({
            "company": context.user_data.get("company", "default"),
            "client_name": context.user_data.get("client_person", "Клиент"),
            "company_name": context.user_data.get("client_org", "Компания"),
            "location": context.user_data.get("location", "Завидово"),
            "manager": f"Ваш менеджер: {update.effective_user.first_name}"
        })

        client_file = estimate_builder.create_excel(response, config.TEMP_PATH, project_info, is_internal=False)
        internal_file = estimate_builder.create_excel(response, config.TEMP_PATH, project_info, is_internal=True)

        with open(client_file, 'rb') as f1:
            await update.message.reply_document(document=f1, caption="📄 Смета для клиента")
        with open(internal_file, 'rb') as f2:
            await update.message.reply_document(document=f2, caption="🔐 Внутренний расчет")

        if os.path.exists(client_file): os.remove(client_file)
        if os.path.exists(internal_file): os.remove(internal_file)
        
    except Exception as e:
        logging.error(f"Ошибка генерации файлов: {e}")
        await update.message.reply_text(f"❌ Ошибка при формировании Excel: {e}")
    
    return await show_main_menu(update, context)

async def handle_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение знаний."""
    save_knowledge(update.message.text)
    await update.message.reply_text("✅ Данные сохранены в базу знаний!")
    return await show_main_menu(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    return await show_main_menu(update, context)

async def process_project_params(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_project_description(update, context)
