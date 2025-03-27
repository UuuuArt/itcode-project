import logging
import os
import sys
import django
from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from django.core.wsgi import get_wsgi_application

from users.models import User

# Определяем корневую папку проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Добавляем корневую папку в sys.path
sys.path.insert(0, BASE_DIR)

# Устанавливаем настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rockrev.settings")

# Инициализируем Django
django.setup()
application = get_wsgi_application()

# Настроим логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TELEGRAM_API_TOKEN = "7585604178:AAF1VHKf8CyVwF0hVwCIW0B0VGiaY2SmexA"


# Функция для получения пользователя по email
def get_user_by_email(email):
    """Синхронная функция для поиска пользователя по email."""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


# Создаем асинхронную обертку для использования синхронной функции
async def async_get_user_by_email(email):
    return await sync_to_async(get_user_by_email)(email)


# Функция для создания нового пользователя или получения уже существующего
def get_or_create_user(user_id):
    """Синхронная функция для получения или создания пользователя по Telegram ID."""
    user, created = User.objects.get_or_create(telegram_id=user_id)
    return user, created


# Асинхронная обертка для создания/получения пользователя
async def async_get_or_create_user(user_id):
    return await sync_to_async(get_or_create_user)(user_id)


# Асинхронная обертка для сохранения пользователя
async def async_save_user(user):
    return await sync_to_async(user.save)()


async def link_telegram_id(update: Update, context: CallbackContext):
    """Команда /link — привязывает Telegram ID к существующему пользователю по email."""
    if not context.args:
        await update.message.reply_text("Пожалуйста, предоставьте свой email, например: /link example@example.com")
        return

    email = context.args[0]  # Берем первый аргумент из команды

    # Ищем пользователя по email
    user = await async_get_user_by_email(email)

    if user:
        # Логируем найденного пользователя
        logging.info(f"Пользователь найден: {user.username} с Telegram ID {user.telegram_id}")

        # Привязываем Telegram ID пользователя
        user.telegram_id = update.message.chat_id
        await async_save_user(user)  # Сохраняем пользователя асинхронно

        await update.message.reply_text(f"Telegram ID успешно привязан к вашему аккаунту: {user.username}")
        await update.message.reply_text(
            "Теперь напишите команду /go, чтобы начать получать уведомления о новых произведениях."
        )
    else:
        # Логируем ошибку, если пользователь не найден
        logging.error(f"Пользователь с email {email} не найден.")

        await update.message.reply_text("Пользователь с таким email не найден. Пожалуйста, проверьте введенные данные.")


async def go(update: Update, context: CallbackContext):
    """Команда /go — пользователь получает уведомления о новых произведениях."""
    user_id = update.message.chat_id

    # Выполняем синхронный запрос к базе через асинхронную обертку
    user, created = await async_get_or_create_user(user_id)

    if created:
        await update.message.reply_text("Привет! Теперь ты будешь получать уведомления о новых произведениях.")
    else:
        await update.message.reply_text("Ты уже зарегистрирован! Будешь получать уведомления.")


async def start(update: Update, context: CallbackContext):
    """Команда /start — инструкция по привязке Telegram ID к аккаунту."""
    await update.message.reply_text(
        "Привет! Чтобы привязать ваш Telegram аккаунт к вашему аккаунту на сайте, используйте команду:\n"
        "/link [ваш email]\n\n"
        "Пример: /link example@example.com"
    )


def main():
    """Запускаем бота."""
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("link", link_telegram_id))
    application.add_handler(CommandHandler("go", go))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()
