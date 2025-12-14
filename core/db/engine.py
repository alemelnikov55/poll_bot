"""
Модуль определения подключения к БД Postre
"""
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from loader import DBSettings

# Создание двигателя и сессии для работы с БД
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '5434')
DATABASE_URL = (
    f'postgresql+asyncpg://{DBSettings.POSTGRES_USER}:{DBSettings.POSTGRES_PASSWORD}'
    f'@{DB_HOST}:{DB_PORT}/{DBSettings.DB_NAME}'
)

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
