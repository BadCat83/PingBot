from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from Config.config import Resource
from FSM.states import ResourceStates, EditResourceStates, AdminState, UnsubscribeState
from Utils.func import create_new_user, get_users, add_user, exit_func, get_resources_list, show_subscribes
from init_bot import dp, bot, db
import Keyboards.keyboards as kb
import ast


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


async def unsubscribe(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'exit':
        async with state.proxy() as data:
            print(data)
        is_admin = 'admin' in (await state.get_state())
        print(f'{is_admin} in unsubscribe')
        await exit_func(callback, state)
        await AdminState.admin.set() if is_admin else await AdminState.user.set()
        return await show_subscribes(callback.message, state)
    else:
        ip, name, *id_list = callback.data.split(',')
        for index, elem in enumerate(id_list):
            id_list[index] = "".join(filter(str.isdecimal, elem))
        id_list.remove(str(callback.from_user.id))
        await db.update_res_users(id_list, ip)
        await callback.message.answer(f"Вы отписались от мониторинга ресурса {name}!",
                                      reply_markup=kb.unsubscribe_kb(await get_resources_list(callback.from_user.id)))
        await callback.answer()
        await callback.message.delete()


async def subscribe_to_resource(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == 'exit':
        await exit_func(callback, state)
        return await AdminState.user.set()
    elif callback.data == 'save_subscribe':
        async with state.proxy() as data:
            for resource in data['resources']:
                await db.update_res_users(resource[1], resource[0])
            await callback.answer("Вы успешно подписались на выбранные ресурсы!")
            await callback.message.delete()
            await state.finish()
            await AdminState.user.set()
    else:
        resource_id, _, users_id = callback.data.split(',')
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
    if callback.data == 'exit':
        await exit_func(callback, state)
        return await AdminState.admin.set()
    async with state.proxy() as data:
        data['resource_ip'], data['resource_name'], _ = callback.data.split(',')
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
    dispatcher.register_callback_query_handler(subscribe_to_resource, state=AdminState.user)
    dispatcher.register_callback_query_handler(unsubscribe, state=[AdminState.admin, AdminState.user,
                                                                   UnsubscribeState.unsubscribe])
    dispatcher.register_callback_query_handler(add_user_to_res, state=EditResourceStates.finish)
    dispatcher.register_callback_query_handler(cancel_query, text='cancel_query', state=AdminState.admin)
