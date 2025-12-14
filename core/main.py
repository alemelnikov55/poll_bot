import asyncio

from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import redis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder


from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command

from loader import MainSettings, WebHookSettings, RedisSettings

from utils.support_commands import start_bot_sup_handler, stop_bot_sup_handler
from utils.filters import IsAdmin
from utils.states import RandomStates

from handlers.poll_answer_handler import handle_poll_answer
from handlers.start_handler import start_handler, fet_id_parse

from handlers.admin.start_poll import start_poll
from handlers.admin.get_polls import get_questions, aplay_kb_handler
from handlers.admin.score_handler import score_handler
from handlers.admin.randon_handler import random_handler
from handlers.admin.random_list import random_list_handler, random_choice

from midlewares.scheduler_middlewares import SchedulerMiddlewares


# r = redis.Redis(host=RedisSettings.REDIS_HOST, port=RedisSettings.REDIS_PORT, db=0, decode_responses=True)
storage = RedisStorage.from_url("redis://redis:6379/0")


dispatcher = Dispatcher(storage=storage)
init_bot = Bot(token=MainSettings.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
apshced = AsyncIOScheduler(timezone="Europe/Moscow")




async def start_bot(bot: Bot, dp: Dispatcher):
    # await bot.delete_webhook()
    dp.startup.register(start_bot_sup_handler)
    dp.shutdown.register(stop_bot_sup_handler)
    # запускаем scheduler
    apshced.start()

    dp.update.middleware.register(SchedulerMiddlewares(apshced))

    dp.callback_query.register(aplay_kb_handler, F.data.startswith('ap_'))

    # dp.message.register(id_parse, F.text)
    dp.message.register(start_handler, Command(commands='start'))
    dp.message.register(fet_id_parse, Command(commands='id'))
    dp.message.register(get_questions, Command(commands='get_questions'), IsAdmin())
    dp.message.register(start_poll, Command(commands='poll'), IsAdmin())

    dp.message.register(random_choice, F.text, RandomStates.GET_USERS)
    dp.message.register(random_list_handler, Command(commands='random_list'), IsAdmin())
    dp.message.register(score_handler, Command(commands='score'), IsAdmin())
    dp.message.register(random_handler, Command(commands='random'), IsAdmin())
    dp.poll_answer.register(handle_poll_answer)
    # dp.message.register(id_parse, F.text)

    # try:
    #     if not WebHookSettings.WEBHOOK_DOMAIN:
    #         await bot.delete_webhook()
    #         await dp.start_polling(
    #             bot,
    #         )
    #     else:
    #
    #         await bot.set_webhook(
    #             url=WebHookSettings.WEBHOOK_DOMAIN + WebHookSettings.WEBHOOK_PATH,
    #             drop_pending_updates=True,
    #             allowed_updates=dp.resolve_used_update_types()
    #         )
    #
    #         app = web.Application()
    #         SimpleRequestHandler(dispatcher=dp,
    #                              bot=bot).register(app, path=WebHookSettings.WEBHOOK_PATH)
    #         runner = web.AppRunner(app)
    #         await runner.setup()
    #         site = web.TCPSite(runner, host=WebHookSettings.APP_HOST, port=WebHookSettings.APP_PORT)
    #         await site.start()
    #
    #         await asyncio.Event().wait()
    # except RuntimeError:
    #     pass
    # finally:
        # await bot.session.close()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start_bot(init_bot, dispatcher))
