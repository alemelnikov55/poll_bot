from random import choice

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.states import RandomStates


async def random_list_handler(message: Message, state: FSMContext):
    """
    Обработчик случайной выборки из списка

    :param message:
    :return:
    """
    await state.set_state(RandomStates.GET_USERS)
    await message.answer('Введите список участников:')


async def random_choice(message: Message, state: FSMContext):
    """
    Обработчик получения случайного участника из списка

    :param message:
    :return:
    """
    fio_list = message.text.split('\n')
    random_user = choice(fio_list)

    await message.answer(f'Победителем становится...\n\n<b>{random_user}</b>', parse_mode='HTML')
    await state.clear()
