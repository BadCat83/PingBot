import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.handler import CancelHandler, current_handler

from DB.sqlite import check_user
from FSM.states import UserStates, AdminState
from Utils.formating import format_ending
from Config.config import BLOCKING_TIME


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: int = BLOCKING_TIME):
        BaseMiddleware.__init__(self)
        self.rate_limit = limit

    async def on_process_message(self, msg: types.Message, data: dict):
        handler = current_handler.get()
        dp = Dispatcher.get_current()

        try:
            await dp.throttle(key='antiflood_message', rate=self.rate_limit)
        except Throttled as _t:
            await self.msg_throttle(msg, _t)
            raise CancelHandler()

        # await self.check_authorization(msg, data['state'])

    # @staticmethod
    # async def check_authorization(msg: types.Message, state: FSMContext):
    #     async with state.proxy() as data:
    #         print(data.state)
    #         if not data.state:
    #             if user_exist := await check_user(msg.from_user.id):
    #                 if user_exist[0]:
    #                     await AdminState.admin.set()
    #                 else:
    #                     await AdminState.user.set()

    @staticmethod
    async def msg_throttle(msg: types.Message, throttled: Throttled):
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count <= 2:
            await msg.reply(f"Вы сможете написать сообщение через {int(delta)} секунд{format_ending(int(delta))}")
        await asyncio.sleep(delta)
