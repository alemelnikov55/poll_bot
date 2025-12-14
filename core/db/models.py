"""
Описание моделей данных для БД и классы данных
"""
from sqlalchemy import Column, Boolean, BigInteger, SmallInteger, String, ARRAY, DateTime, Time, func
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class Answers(Base):
    """
    Класс определения таблицы answers для записи правильных ответов пользователей
    """
    __tablename__ = 'answers'

    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    poll_id = Column(String, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    answer_duration = Column(Time, nullable=True)


class PollQuestions(Base):
    __tablename__ = 'polls'

    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)
    options = Column(ARRAY(String), nullable=False)
    correct_answer_id = Column(SmallInteger, nullable=False)
    image_url = Column(String, nullable=False)
    poll_id = Column(String, nullable=True)
    start_time = Column(DateTime, default=None, nullable=True)
    is_done = Column(Boolean, default=False)
