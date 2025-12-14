from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


async def test_handler(message: Message, state: FSMContext, bot: Bot):
    poll_data = await state.get_data()
    print(poll_data)
