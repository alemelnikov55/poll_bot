from typing import List

from aiogram import Bot
from aiogram.types import Message

from db.engine import async_session
from db.requests import AnswersRequests
from loader import MainSettings, LocalProjectSettings


async def score_handler(message: Message, bot: Bot):
    """
    Обработка команды /score

    Выводит рейтинг пользователей с максимальным количеством праильных ответов.
    :param message:
    :return:
    """
    admin_text_message = []
    text_message: List[str] = []
    # Получаем рейтинг пользователей с максимальным количеством ответов
    async with async_session() as session:
        await AnswersRequests.update_answer_durations(session)
        scores = await AnswersRequests.get_user_statistics(session)
    # Отправляем результаты в чат
    await message.answer('Топ 5 пользователей:')
    for user_id, count, duration in scores:
        user = await bot.get_chat_member(LocalProjectSettings.GROUP_ID, user_id)
        if user.user.username:
            username = user.user.username
        else:
            username = user.user.full_name

        admin_username = ''
        if user.user.username:
            admin_username += user.user.username
        if user.user.full_name:
            admin_username += ' '
            admin_username += user.user.full_name

        admin_text_message.append(f'@{admin_username}: {count} за {duration}. ID: {user_id}')
        text_message.append(f'{username}: {count} за {duration}')

    for id_ in MainSettings.ADMIN_LIST:
        await bot.send_message(id_, '\n'.join(admin_text_message))

    # await message.answer('\n'.join(text_message))
