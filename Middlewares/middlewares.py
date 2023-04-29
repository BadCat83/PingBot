import asyncio
from aiogram import types, Dispatcher

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.handler import CancelHandler, current_handler

from Utils.formating import format_ending
from Config.config import BLOCKING_TIME

"""Some middlewares"""


class ThrottlingMiddleware(BaseMiddleware):
    """Anti flood handler"""
    def __init__(self, limit: int = BLOCKING_TIME):
        BaseMiddleware.__init__(self)
        self.rate_limit = limit

    async def on_process_message(self, msg: types.Message, data: dict):
        dp = Dispatcher.get_current()

        try:
            await dp.throttle(key='antiflood_message', rate=self.rate_limit)
        except Throttled as _t:
            await self.msg_throttle(msg, _t)
            raise CancelHandler()

    @staticmethod
    async def msg_throttle(msg: types.Message, throttled: Throttled):
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count <= 2:
            await msg.reply(f"Вы сможете написать сообщение через {int(delta)} секунд{format_ending(int(delta))}")
        await asyncio.sleep(delta)
