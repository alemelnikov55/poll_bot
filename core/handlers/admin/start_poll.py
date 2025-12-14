import time
from datetime import datetime, timedelta

from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from loader import LocalProjectSettings, MainSettings
from db.storage import Storage
from db.requests import PollRequests, AnswersRequests
from db.engine import async_session


async def start_poll(message: Message, bot: Bot, scheduler: AsyncIOScheduler):
    """
    Обработка команды /poll

    Забирает опрос из БД, и отправляет в чат с участниками.
    :param scheduler:
    :param bot:
    :return:
    """
    async with async_session() as session:
        number_of_poll = await PollRequests.get_next_pending_poll(session)
        # poll_data = await PollRequests.get_poll_question(session, number_of_poll.id)
    await bot.send_photo(LocalProjectSettings.GROUP_ID, number_of_poll.image_url)
    poll = await bot.send_poll(
        chat_id=LocalProjectSettings.GROUP_ID,
        question=number_of_poll.question,
        options=number_of_poll.options,
        is_anonymous=False,
        open_period=LocalProjectSettings.TIME_FOR_ANSWER,
        allows_multiple_answers=False,
        type='regular'
    )
    correct_answer: int = number_of_poll.correct_answer_id - 1
    Storage.correct_answers[poll.poll.id] = correct_answer
    scheduler.add_job(insert_all_correct_answers,
                      trigger='date',
                      next_run_time=datetime.now() + timedelta(seconds=LocalProjectSettings.TIME_FOR_ANSWER + 10),
                      kwargs={'bot': bot, 'poll_id': number_of_poll.id})
    # записываем данные о текущем опросе
    async with async_session() as session:
        await PollRequests.update_poll(session, poll.poll.id, datetime.now(), number_of_poll.id)


async def insert_all_correct_answers(bot: Bot, poll_id: int):
    async with async_session() as session:
        await AnswersRequests.insert_answer(session, Storage.answers_list)
        await PollRequests.mark_poll_as_done(session, poll_id)
    # Очищаем лист для заполнения
    time.sleep(1)
    Storage.answers_list.clear()
    for id_ in MainSettings.ADMIN_LIST:
        await bot.send_message(id_, 'Шалость удалась')
    print('Данные загружены')
