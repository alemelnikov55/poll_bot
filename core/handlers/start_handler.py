"""
Обработчик команды /start - регистрация пользователя в БД
"""
from aiogram import Bot
from aiogram.types import Message, BotCommand, BotCommandScopeChat

# from database.engine import async_session
# from database.requests import UserService


async def start_handler(message: Message, bot: Bot):
    """
    Обработчик команды /start - регистрация пользователя в БД

    :param message:
    :param bot:
    :return:
    """
    user_id = message.from_user.id

    if not message.from_user.full_name:
        user_name = message.from_user.username
    else:
        user_name = message.from_user.full_name

    # Добавляем пользователя в БД и устанавливаем его команды
    # async with async_session() as session:
    #     await UserService.add_user(session, user_id, user_name)

    await message.answer(f'Привет, {user_name}!\n')


async def fet_id_parse(message: Message):
    id = message.chat.id
    await message.answer(f'id группы: {id}')