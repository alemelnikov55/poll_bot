"""
Модуль констант для работы бота
"""
import dataclasses
import os

from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit('Файл .env не найден. Переменные не загружены')
else:
    load_dotenv()


@dataclasses.dataclass
class MainSettings:
    TOKEN = os.getenv('TOKEN')
    SUPERUSER = int(os.getenv('SUPERUSER'))
    ADMIN_LIST = [int(x) for x in os.getenv('ADMIN_LIST').split(' ')]


class DBSettings:
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')


class LocalProjectSettings:
    GROUP_ID = int(os.getenv('GROUP_ID'))
    TIME_FOR_ANSWER = int(os.getenv('TIME_FOR_ANSWER'))


class TableSettings:
    TABLE_NAME = os.getenv('TABLE_NAME')
    LIST_NAME = os.getenv('LIST_NAME')


class RedisSettings:
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = os.getenv('REDIS_PORT')

class WebHookSettings:
    WEBHOOK_DOMAIN = os.getenv('WEBHOOK_DOMAIN')
    WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
    APP_PORT = os.getenv('APP_PORT')
    APP_HOST = os.getenv('APP_HOST')
