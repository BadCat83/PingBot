from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from Config.config import Resource
from FSM.states import ResourceStates, EditResourceStates, AdminState, SubscribeState
from Utils.func import create_new_user, get_users, add_user, exit_func, get_resources_list, show_subscribes
from init_bot import dp, bot, db, resources_storage
import Keyboards.keyboards as kb
import ast
import re

"""Callback handlers"""


async def add_new_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handles the create new user command"""
    await create_new_user(callback, bot, state, dp)


async def add_new_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handles the create new user command as an admin"""
    await create_new_user(callback, bot, state, dp, is_administrator=True)


async def cancel_query(callback: types.CallbackQuery):
    """Cancels any action"""
    await create_new_user(callback, bot)


async def add_resource(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handles the create new resource command"""
    # Creating a new resource with adding new users to it with a kind of loop
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
                # Adding the resource to monitoring
                resources_storage.lpush('res', str(resource.ip_address))
                resources_storage.hmset(str(resource.ip_address), {'avail': 1, 'dt': ' ', 'cnt': 0})
                await callback.message.answer(f"Ресурс {data['resource_name']} "
                                              f"с ip адресом {data['ip_address']} успешно создан",
                                              reply_markup=kb.admin_kb())
            finally:
                await callback.message.delete()
                await callback.answer("Успешное добавление ресурса!")
                await state.finish()
                await AdminState.admin.set()
    else:
        # While the save button won't be pressed, adding a new user to the created resource
        await add_user(callback, state)


async def unsubscribe(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handles the unsubscribe command"""
    # While the exit button won't be pressed, continuing to unsubscribe of the resources
    if callback.data == 'exit':
        is_admin = 'admin' in (await state.get_state())
        await exit_func(callback, state)
        await AdminState.admin.set() if is_admin else await AdminState.user.set()
        return await show_subscribes(callback.message, state)
    else:
        ip, name, ids = callback.data.split('|')
        id_list = re.findall(r'\d+', ids)
        id_list.remove(str(callback.from_user.id))
        await db.update_res_users(id_list, ip)
        await callback.message.answer(f"Вы отписались от мониторинга ресурса {name}!",
                                      reply_markup=kb.unsubscribe_kb(await get_resources_list(callback.from_user.id)))
        await callback.answer()
        await callback.message.delete()


async def subscribe_to_resource(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handles the subscribe command"""
    # Stopping to subscribe handling and resetting to subscribe state
    if callback.data == 'exit':
        await exit_func(callback, state)
        return await AdminState.user.set()
    # Subscribing to the selected resource
    elif callback.data == 'save_subscribe':
        async with state.proxy() as data:
            for resource in data['resources']:
                await db.update_res_users(resource[1], resource[0])
            await callback.answer("Вы успешно подписались на выбранные ресурсы!")
            await callback.message.delete()
            await state.finish()
            await AdminState.user.set()
    # Adding resources to the list of the subscribes
    else:
        resource_id, _, users_id = callback.data.split('|')
        users_id = ast.literal_eval(users_id)
        users_id.append(str(callback.from_user.id))
        async with state.proxy() as data:
            data['resources'].append((resource_id, users_id))
            for element in data['resources_list']:
                if element[0] == resource_id:
                    data['resources_list'].remove(element)
                    break
            await callback.message.delete()
            await callback.message.answer('Выберите ресурс на который хотите подписаться',
                                          reply_markup=kb.add_users_to_res_kb(data['resources_list']))
        await callback.answer()


async def choose_resource(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handles the adding_user_to_resource command. This handler is allowed only for users with the admin rights"""
    if callback.data == 'exit':
        await exit_func(callback, state)
        return await AdminState.admin.set()
    async with state.proxy() as data:
        data['resource_ip'], data['resource_name'], _ = callback.data.split('|')
        data["users_list"], data["current_users"] = await get_users(data['resource_ip'])

    if not data["users_list"]:
        await callback.answer("Все возможные пользователи уже мониторят этот ресурс!")
    else:
        await callback.message.delete()
        await callback.message.answer("Добавьте нужных пользователей в список.",
                                      reply_markup=kb.choose_users_kb(data["users_list"]))
        await EditResourceStates.next()
        await callback.answer("Ресурс выбран, добавьте пользователей!")


async def add_user_to_res(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handles adding users to the resource after creating the resource by admin"""
    if callback.data == 'save':
        async with state.proxy() as data:
            if 'users_id' in data.keys():
                try:
                    await db.update_res_users(data['users_id'] + data["current_users"], data['resource_ip'])
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
                    await callback.answer(
                        f"Все назначенные пользователи теперь мониторят ресурс {data['resource_name']}!")
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
    dispatcher.register_callback_query_handler(subscribe_to_resource, state=SubscribeState.subscribe)
    dispatcher.register_callback_query_handler(unsubscribe, state=[AdminState.admin, AdminState.user])
    dispatcher.register_callback_query_handler(add_user_to_res, state=EditResourceStates.finish)
    dispatcher.register_callback_query_handler(cancel_query, text='cancel_query', state=AdminState.admin)
