import random

from aiogram import Bot
from aiogram.types import Message

from db.engine import async_session
from db.requests import AnswersRequests


async def random_handler(message: Message, bot: Bot):
    """
    Обработчик команды /random

    выбирает случайного пользователя из всех участников
    :param message:
    :param bot:
    :return:
    """
    async with async_session() as session:
        all_users = await AnswersRequests.get_all_users(session)

    winner_id = random.choice(all_users)

    user = await bot.get_chat_member(-4282387398, winner_id)
    if user.user.full_name:
        username = user.user.full_name
    else:
        username = user.user.username

    await message.answer(f'Счастливчиком становится....\n{username}')

