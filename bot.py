import asyncio

from aiogram import executor
from Middlewares.middlewares import ThrottlingMiddleware
from Utils.func import authorization_on_startup
from Utils.ping_logic import do_ping
from init_bot import dp, db

from Handlers import callback_handlers, message_handlers

"""Start functions"""


async def on_startup(_):
    """Initializes database and authorizes users"""
    await db.db_start()
    await authorization_on_startup(dp)


callback_handlers.register_callback_handlers(dp)
message_handlers.register_message_handlers(dp)


def bot_start() -> None:
    """Setups anti-spam middleware, creates ping task and starts the bot"""
    dp.middleware.setup(ThrottlingMiddleware())
    loop = asyncio.get_event_loop()
    loop.create_task(do_ping())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    bot_start()
