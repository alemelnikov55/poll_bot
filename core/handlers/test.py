
app = web.Application()    # Настраиваем обработчик запросов для работы с вебхуком
webhook_requests_handler = SimpleRequestHandler(
    dispatcher=dp,  # Передаем диспетчер
    bot=bot  # Передаем объект бота
    )    # Регистрируем обработчик запросов на определенном пути
webhook_requests_handler.register(app, path=WEBHOOK_PATH)
# Настраиваем приложение и связываем его с диспетчером и ботом
setup_application(app, dp, bot=bot)    # Запускаем веб-сервер на указанном хосте и порте
web.run_app(app, host=HOST, port=PORT)