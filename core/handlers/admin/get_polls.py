"""
Модуль получения вопросов из GoogleSheets и записи их в БД проекта
"""
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.exc import DBAPIError

from db.requests import PollRequests, ServiceRequests
from db.engine import async_session
from db.storage import Storage
from loader import TableSettings
from utils.goolge_sheets.google_sheets_parser import get_sheet_task_data


async def get_questions(message: Message):
    """
    Обработчик команды /get_questions

    Скачивает данные из GoogleSheets, заливает данные в БД для использования
    :param message:
    :return:
    """
    await message.answer(
        f'Вы уверены, что хотите загрузить новые вопросы? Все данные о предыдущих событиях будут удалены.',
        reply_markup=aplay_kb_builder()
    )


async def load_question_to_db() -> int:
    """
    Загрузка вопросов из Google Sheets в БД
    """
    questions_list = []
    google_data = await get_sheet_task_data(TableSettings.LIST_NAME)
    # google_data = [{'вопрос': 'Факт про человека', 'варианты ответа': 'Петров Петр \nАлексеев Алексей Алексеич\nТетя Маша', 'номер правильного ответа': 3, 'ссфлка на фото': 'https://content.foto.my.mail.ru/mail/alemel/_myphoto/h-66.jpg'}, {'вопрос': 'Этого человека завораживает вид нашей Земли с высоты, он засыпает с видом из окна с 80 м. высоты. Какое-то время этот человек даже жил на высоте 2350 м. над уровнем моря. Ваш коллега прыгал из вертолета на высоте 800 м. и в 2022 году взбирался на высоту 4700 м. над уровнем моря.', 'варианты ответа': 'Колесов Евгений\nИванов Иван \nКлепакова Екатерина ', 'номер правильного ответа': 3, 'ссфлка на фото': 'https://content.foto.my.mail.ru/mail/alemel/_myphoto/h-67.jpg'}]

    for question in google_data:
        question_data = list(question.values())
        questions_list.append((question_data[0], question_data[1].split('\n'), question_data[2], question_data[3]))
    async with async_session() as session:
        await PollRequests.insert_poll_questions(session, questions_list)
    return len(questions_list)


def aplay_kb_builder() -> InlineKeyboardMarkup:
    """
    Генератаор клавиатуры для подтверждения отправки опроса

    :return: InlineKeyboardMarkup
    """
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='ДА ✅', callback_data='ap_y')
    keyboard_builder.button(text='НЕТ ❌', callback_data='ap_n')
    keyboard = keyboard_builder.as_markup()
    return keyboard


async def aplay_kb_handler(call: CallbackQuery):
    """

    :param call:
    :return:
    """
    answer = call.data.split('_')[1]
    if answer == 'y':
        # Отчищаем базу вопросов от предыдущих записей
        await ServiceRequests.clear_question_table()
        # Загружаем данные из Google Sheets и заливаем в БД
        try:
            poll_quantity = await load_question_to_db()
        except DBAPIError as e:
            await call.message.answer('Ошибка при работе с базой данных, попробуйте позже')
            print(e)
            return
        Storage.polls_id_list = [i for i in range(1, poll_quantity + 1)]
        await call.message.answer(f'Загрузка вопросов завершена. Всего загружено {poll_quantity} вопросов.')
        await call.answer(text='Загрузка завершена')
