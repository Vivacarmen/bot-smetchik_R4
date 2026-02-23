import sys
import os

# Добавляем родительскую папку в путь для поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ConversationHandler
)

# Импорты из пакета bot
from bot import config
from bot import handlers

# Настройка логирования для отслеживания работы бота
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
# Снижаем уровень шума от библиотеки httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    """
    Основная функция запуска бота.
    Инициализирует базу данных и настраивает диспетчер команд.
    """
    # 1. Инициализируем базу данных (создаем таблицу, если её нет)
    handlers.init_db()
    
    # 2. Создаем экземпляр приложения Telegram
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # 3. Настраиваем ConversationHandler для пошагового опроса
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handlers.start)],
        states={
            handlers.AUTH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_auth)
            ],
            handlers.MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_menu_choice)
            ],
            handlers.SELECT_COMPANY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.select_company)
            ],
            handlers.CLIENT_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_client_details)
            ],
            handlers.COMPANY_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_company_name)
            ],
            handlers.LOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_location)
            ],
            handlers.PROJECT_PARAMS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.process_project_params)
            ],
            handlers.TRAINING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_training)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', handlers.cancel),
            CommandHandler('start', handlers.start)
        ],
        allow_reentry=True
    )
    
    # 4. Регистрация обработчика в приложении
    application.add_handler(conv_handler)
    
    # 5. Запуск цикла получения обновлений (Polling)
    print("--- Бот успешно запущен ---")
    print("Версия: Groq AI, структура: /root/projects/py/")
    application.run_polling()

if __name__ == '__main__':
    main()
