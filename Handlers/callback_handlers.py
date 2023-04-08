from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from Utils.func import create_new_user
from init_bot import dp, bot


async def add_new_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    await create_new_user(callback, bot, state, dp)


async def add_new_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    await create_new_user(callback, bot, state, dp, is_administrator=True)


async def cancel_query(callback: types.CallbackQuery):
    await create_new_user(callback, bot)


def register_callback_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(add_new_user, text='add_as_user')
    dispatcher.register_callback_query_handler(add_new_admin, text='add_as_admin')
    dispatcher.register_callback_query_handler(cancel_query, text='cancel_query')
