from datetime import datetime

from aiogram.types import PollAnswer
from db.storage import Storage


async def handle_poll_answer(poll_answer: PollAnswer):
    if poll_answer.option_ids[0] == Storage.correct_answers[poll_answer.poll_id] or Storage.correct_answers[poll_answer.poll_id] >= 5:
        Storage.answers_list.append((poll_answer.poll_id, poll_answer.user.id, datetime.now()))
