"""
Вспомогательные команды для оповещения администратора и страта бота
"""
from db.requests import ServiceRequests


async def start_bot_sup_handler() -> None:
    """Запуск бота

    Отправляет сообщение админимтратору и запускает процесс создания и проверки БД
    """
    await ServiceRequests.init_db()
    print('Bot started')


async def stop_bot_sup_handler() -> None:
    """Остановка бота"""
    print('Bot stopped')
