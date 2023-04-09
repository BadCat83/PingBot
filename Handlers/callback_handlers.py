from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from Config.config import Resource
from FSM.states import ResourceStates
from Keyboards.keyboards import choose_users_kb
from Utils.func import create_new_user
from init_bot import dp, bot, db
import Keyboards.keyboards as kb


async def add_new_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    await create_new_user(callback, bot, state, dp)


async def add_new_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    await create_new_user(callback, bot, state, dp, is_administrator=True)


async def cancel_query(callback: types.CallbackQuery):
    await create_new_user(callback, bot)


async def add_resource(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data.startswith('add_user'):
        user_id = callback.data.split('_')[2]
        async with state.proxy() as data:
            if 'users_id' not in data:
                data['users_id'] = [user_id, ]
            else:
                data['users_id'].append(user_id)
            for user in data['users_list']:
                if user_id in user:
                    data['users_list'].remove(user)
                    await callback.message.answer(f"Пользователь {user[2]} добавлен наблюдателем за ресурсом"
                                                  f" {data['resource_name']}.",
                                                  reply_markup=await choose_users_kb(data['users_list']))
                    break
        await callback.message.delete()
        await callback.answer()
    else:
        async with state.proxy() as data:
            resource = Resource(
                resource_name=data['resource_name'],
                ip_address=data['ip_address'],
                describe=data['describe'],
                users_id=data['users_id'] if 'users_id' in data else []
            )
            try:
                await db.create_resource(resource)
            except Exception as e:
                await callback.message.answer(
                    f"При создании ресурса возникла следующая ошибка - {e}. Попробуйте еще раз!",
                    reply_markup=kb.admin_kb())
            else:
                await callback.message.reply(f"Ресурс {data['resource_name']} "
                                             f"с ip адресом {data['ip_address']} успешно создан",
                                             reply_markup=kb.admin_kb())
            finally:
                await callback.message.delete()
                await callback.answer()
                await state.finish()


def register_callback_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(add_new_user, text='add_as_user')
    dispatcher.register_callback_query_handler(add_new_admin, text='add_as_admin')
    dispatcher.register_callback_query_handler(add_resource, state=ResourceStates.add_users)
    dispatcher.register_callback_query_handler(cancel_query, text='cancel_query')
