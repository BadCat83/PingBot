from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from Config.config import Resource
from FSM.states import ResourceStates, EditResourceStates, AdminState
from Keyboards.keyboards import choose_users_kb
from Utils.func import create_new_user, get_users, add_user
from init_bot import dp, bot, db
import Keyboards.keyboards as kb


async def add_new_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    await create_new_user(callback, bot, state, dp)


async def add_new_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    await create_new_user(callback, bot, state, dp, is_administrator=True)


async def cancel_query(callback: types.CallbackQuery):
    await create_new_user(callback, bot)


async def add_resource(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'save':
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
                await callback.message.answer(f"Ресурс {data['resource_name']} "
                                              f"с ip адресом {data['ip_address']} успешно создан",
                                              reply_markup=kb.admin_kb())
            finally:
                await callback.message.delete()
                await callback.answer("Успешное добавление ресурса!")
                await state.finish()
                await AdminState.admin.set()
    else:
        await add_user(callback, state)


async def choose_resource(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'exit':
        await callback.message.delete()
        await callback.answer()
        await state.finish()
        return await AdminState.admin.set()
    async with state.proxy() as data:
        data['resource_ip'], data['resource_name'] = callback.data.split(',')
        data["users_list"], data["current_users"] = await get_users(data['resource_ip'])

    if not data["users_list"]:
        await callback.answer("Все возможные пользователи уже мониторят этот ресурс!")
    else:
        await callback.message.delete()
        await callback.message.answer("Добавьте нужных пользователей в список.",
                                      reply_markup=await kb.choose_users_kb(data["users_list"]))
        await EditResourceStates.next()
        await callback.answer("Ресурс выбран, добавьте пользователей!")


async def add_user_to_res(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'save':
        async with state.proxy() as data:
            if 'users_id' in data.keys():
                try:
                    await db.add_users_to_res(data['users_id'] + data["current_users"], data['resource_ip'])
                except Exception as e:
                    await callback.message.answer(
                        f"При добавлении пользователя возникла следующая ошибка - {e}. Попробуйте еще раз!",
                        reply_markup=kb.admin_kb())
                else:
                    await callback.message.answer(f"Все добавленные пользователи теперь мониторят ресурс "
                                                  f"{data['resource_name']} с ip адресом {data['resource_ip']}",
                                                  reply_markup=kb.admin_kb())
                finally:
                    await callback.message.delete()
                    await callback.answer(f"Все назначенные пользоватлели теперь мониторят ресурс {data['resource_name']}!")
                    # await state.finish()
                    # await AdminState.admin.set()
            else:
                await callback.message.delete()
                await callback.message.answer("Вы не выбрали ни одного пользователя!", reply_markup=kb.admin_kb())
        await state.finish()
        await AdminState.admin.set()
    else:
        await add_user(callback, state)


def register_callback_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(add_new_user, text='add_as_user', state=AdminState.admin)
    dispatcher.register_callback_query_handler(add_new_admin, text='add_as_admin', state=AdminState.admin)
    dispatcher.register_callback_query_handler(add_resource, state=ResourceStates.add_users)
    dispatcher.register_callback_query_handler(choose_resource, state=EditResourceStates.add_user)
    dispatcher.register_callback_query_handler(add_user_to_res, state=EditResourceStates.finish)
    dispatcher.register_callback_query_handler(cancel_query, text='cancel_query', state=AdminState.admin)
