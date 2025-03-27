from django.db.models.signals import m2m_changed
import asyncio
from telegram import Bot
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from reviews.models import Title, FollowBand
from users.models import Profile, User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Автоматически создает профиль для нового пользователя."""
    if created:
        Profile.objects.create(user=instance)


# Асинхронная функция для отправки сообщения в Telegram
async def send_telegram_message(chat_id, text):
    bot = Bot(token=settings.TG_API_TOKEN)
    await bot.send_message(chat_id=chat_id, text=text)


# Обертка для вызова асинхронной функции из синхронного кода
def send_notification(chat_id, text):
    asyncio.run(send_telegram_message(chat_id, text))


@receiver(m2m_changed, sender=Title.band.through)
def notify_new_title_m2m(sender, instance, action, **kwargs):
    if action == 'post_add':
        print(f"m2m_changed: новые группы добавлены для тайтла: {instance.name}")
        for band in instance.band.all():
            print(f"Обрабатываем группу: {band.name}")
            followers = FollowBand.objects.filter(following_band=band).select_related('user')
            for follower in followers:
                print(f"Найден подписчик: {follower.user.username}")
                user = follower.user
                telegram_id = user.telegram_id
                if telegram_id:
                    message = f"Новое произведение от группы {band.name}: {instance.name}"
                    try:
                        send_notification(telegram_id, message)
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения: {e}")
                else:
                    print(f"Telegram ID не найден для пользователя {user.username}")
