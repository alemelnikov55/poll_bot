"""
Модуль определения запросов к БД
Запросы преимущественно пишутся под конкретную задачу и используются только для нее
Запросы реализованы через методы классов и разделены по месту|таблице применения
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Tuple

from sqlalchemy import text, func, update, inspect, Table, Column, desc, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from db.engine import async_session, engine
from db.models import Base, PollQuestions, Answers


class ServiceRequests:
    """
    Класс асинхронных сервисных команды для поддержки БД
    """

    @staticmethod
    async def init_db():
        """
        Создание таблиц в базе данных PostgreSQL
        """
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def drop_db():
        """
        Удаление таблиц из базы данных PostgreSQL
        """
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @staticmethod
    async def clear_question_table():
        """
        Очистка таблиц polls и answers
        """
        async with engine.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE polls, answers RESTART IDENTITY CASCADE"))
            print('Table poll cleared')


class PollRequests:
    """
    Класс асинхронных запросов к таблице polls
    """

    @staticmethod
    async def insert_poll_questions(session: AsyncSession, data: List[Tuple[str, List[str], int, str]]):
        """
        Вставляет данные в таблицу polls

        :param session: AsyncSession Сессия для работы с БД
        :param data: list[Tuple[str, List[str], int, str]] Список кортежей с вопросом, вариантами ответа и номером правильного ответа
        """
        # Создаем список объектов PollQuestions
        poll_questions = [
            PollQuestions(question=question, options=options, correct_answer_id=correct_answer_id, image_url=url)
            for question, options, correct_answer_id, url in data
        ]

        # Вставляем данные в таблицу
        async with session.begin():
            session.add_all(poll_questions)
            await session.commit()

    @staticmethod
    async def get_poll_question(session: AsyncSession, poll_id: int) -> PollQuestions:
        """
        Получение вопроса из таблицы polls по идентификатору

        :param session: AsyncSession Сессия для работы с БД
        :param poll_id: int Идентификатор вопроса
        :return: PollQuestions|None
        """
        print(poll_id)
        query = select(PollQuestions).where(PollQuestions.id == poll_id)
        result = await session.execute(query)
        poll = result.scalars().first()
        return poll

    @staticmethod
    async def mark_poll_as_done(session: AsyncSession, poll_id: int):
        """
        Изменяет поле is_done на True для записи с указанным id.

        :param session: Асинхронная сессия SQLAlchemy для взаимодействия с БД
        :param poll_id: ID записи, которую нужно обновить
        :return: True, если запись обновлена, False, если запись не найдена
        """
        print(poll_id)
        result = await session.execute(
            update(PollQuestions)
            .where(PollQuestions.id == poll_id)
            .values(is_done=True)
            .execution_options(synchronize_session="fetch")
        )
        if result.rowcount == 0:
            return False  # Запись не найдена
        await session.commit()
        return True

    @staticmethod
    async def get_next_pending_poll(session: AsyncSession):
        """
        Выбирает запись с наименьшим значением id, у которой is_done = False.

        :param session: Асинхронная сессия SQLAlchemy для взаимодействия с БД
        :return: Объект PollQuestions или None, если таких записей нет
        """
        result = await session.execute(
            select(PollQuestions)
            .where(PollQuestions.is_done == False)
            .order_by(PollQuestions.id.asc())
            .limit(1)
        )
        return result.scalars().first()

    @staticmethod
    async def update_poll(session: AsyncSession, poll_id: str, start_time: datetime, poll_record_id: int):
        """
        Обновляет запись в таблице PollQuestions по указанному id.

        :param session: Асинхронная сессия SQLAlchemy для взаимодействия с БД
        :param poll_id: Новое значение для поля poll_id
        :param start_time: Новое значение для поля start_time
        :param poll_record_id: ID записи, которую нужно обновить
        :return: True, если запись обновлена, False, если запись не найдена
        """
        result = await session.execute(
            update(PollQuestions)
            .where(PollQuestions.id == poll_record_id)
            .values(
                poll_id=poll_id,
                start_time=start_time
            )
            .execution_options(synchronize_session="fetch")
        )
        if result.rowcount == 0:
            return False  # Запись с указанным ID не найдена

        await session.commit()
        return True


class AnswersRequests:
    """
    Класс асинхронных запросов к таблице answers
    """

    @staticmethod
    async def insert_answer(session: AsyncSession, answers_list: List[Tuple[str, int, datetime]]):
        """
        Вставляет данные в таблицу answers

        :param session: AsyncSession Сессия для работы с БД
        :param answers_list: List[Tuple[str, int]] Список id_poll, user_id
        """
        # Создаем объекты Answers
        answers_list = [Answers(poll_id=poll_id, user_id=user_id, timestamp=time) for poll_id, user_id, time in answers_list]

        # Вставляем данные в таблицу
        session.add_all(answers_list)
        await session.commit()

    @staticmethod
    async def get_scores(session: AsyncSession, limit=5):
        """
        Получает пользователей с максимальным количеством ответов в таблице answers.

        :param session: Экземпляр AsyncSession.
        :param limit: Количество записей, которые нужно вернуть (по умолчанию 5).
        :return: Список кортежей (user_id, count).
        """
        # Запрос для подсчёта повторений user_id
        query = (
            select(Answers.user_id, func.count(Answers.user_id).label('count'))
            .group_by(Answers.user_id)
            .order_by(desc('count'))
            .limit(limit)
        )

        # Выполнение запроса
        result = await session.execute(query)
        return result.fetchall()

    @staticmethod
    async def   get_user_statistics(session: AsyncSession):
        """
        Вычисляет статистику для пользователей:
        - Количество записей в таблице answers
        - Суммарное время из answer_duration
        Игнорирует ответы на первый вопрос (PollQuestions.id = 1).
        Возвращает 5 записей, отсортированных по убыванию количества записей и увеличению суммарного времени.

        :param session: Асинхронная сессия SQLAlchemy для взаимодействия с БД
        :return: Список из 5 записей в формате (user_id, количество записей, суммарное время)
        """
        # Создаём алиас для таблицы PollQuestions
        poll_alias = aliased(PollQuestions)

        result = await session.execute(
            select(
                Answers.user_id,
                func.count(Answers.id).label("record_count"),
                func.sum(func.extract('epoch', Answers.answer_duration)).label("total_duration")
            )
            .join(poll_alias, poll_alias.poll_id == Answers.poll_id)  # Соединяем таблицы
            .where(poll_alias.id != 1)  # Игнорируем ответы на первый вопрос
            .group_by(Answers.user_id)
            .order_by(
                func.count(Answers.id).desc(),  # Сортировка по убыванию количества записей
                func.sum(func.extract('epoch', Answers.answer_duration)).asc()
                # Сортировка по возрастанию суммарного времени
            )
            .limit(5)  # Лимит на 5 записей
        )

        # Преобразуем результат в список
        data = [
            (user_id, record_count, total_duration)
            for user_id, record_count, total_duration in result.fetchall()
        ]
        return data

    @staticmethod
    async def get_all_users(session: AsyncSession):
        """
        Получает список всех уникальных значений из столбца user_id.

        :param session: Экземпляр AsyncSession.
        :return: Список уникальных user_id.
        """
        # Создание запроса для выборки уникальных значений user_id
        query = select(distinct(Answers.user_id))

        # Выполнение запроса
        result = await session.execute(query)

        # Извлечение всех уникальных значений
        unique_user_ids = [row[0] for row in result.fetchall()]
        return unique_user_ids

    @staticmethod
    async def update_answer_durations(session: AsyncSession):
        """
        Вычисляет и обновляет поле answer_duration в таблице answers.
        Разница между start_time (PollQuestions) и timestamp (Answers).

        :param session: Асинхронная сессия SQLAlchemy для взаимодействия с БД
        """
        # Подзапрос для получения пар poll_id и start_time из таблицы PollQuestions
        poll_start_time_subquery = select(
            PollQuestions.poll_id, PollQuestions.start_time
        ).subquery()

        # Основной запрос для обновления answer_duration
        result = await session.execute(
            update(Answers)
            .where(
                Answers.poll_id == poll_start_time_subquery.c.poll_id  # Связываем по poll_id
            )
            .values(
                answer_duration=text("answers.timestamp - anon_1.start_time")  # Используем текст SQL напрямую
            )
            .execution_options(synchronize_session="fetch")
        )

        # Если строки были обновлены, фиксируем изменения
        if result.rowcount > 0:
            await session.commit()

#
# if __name__ == '__main__':
#     asyncio.run(ServiceRequests.drop_db())
