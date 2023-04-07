from aiogram import executor
from Middlewares.middlewares import ThrottlingMiddleware
from init_bot import dp
from Handlers.message_handlers import db

from Handlers import callback_handlers, message_handlers


async def on_startup(_):
    await db.db_start()


callback_handlers.register_callback_handlers(dp)
message_handlers.register_message_handlers(dp)


def bot_start() -> None:
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    bot_start()
