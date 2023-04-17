import ast

from aiogram import types, Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from DB.sqlite import create_user, check_users_exist, get_resource_users, get_resources
from FSM.states import UserStates, AdminState
from Keyboards.keyboards import admin_kb, choose_users_kb


def return_user_data(user: types.User) -> tuple:
    return user.id, user.username, user.full_name


async def authorization_on_startup(dp: Dispatcher):
    for user in await check_users_exist():
        state = dp.current_state(chat=user[0], user=user[0])
        await state.set_state(AdminState.admin if user[3] else AdminState.user)


async def create_new_user(
        callback: types.CallbackQuery,
        bot: Bot,
        state: FSMContext = None,
        dp: Dispatcher = None,
        is_administrator=False
) -> None:
    user_id = callback.message.text.split('"')[1]
    if state:
        data = await state.storage.get_data(chat=user_id, user=user_id)
        data['user'].is_administrator = is_administrator
        await create_user(data['user'])
        await callback.message.answer(
            f"Пользователь {data['user'].user_name} добавлен в качестве "
            f"{'пользователя' if not is_administrator else 'администратора'} системы.", reply_markup=admin_kb())
        state = dp.current_state(chat=user_id, user=user_id)
        await state.set_state(AdminState.admin if is_administrator else AdminState.user)
    else:
        user_name = (await bot.get_chat_member(chat_id=user_id, user_id=int(user_id))).user.full_name
        await callback.message.answer(f'Вы отклонили запрос пользователя {user_name}')
    await callback.message.delete()
    if state:
        await bot.send_message(user_id,
                               f"Администратор {callback.from_user.full_name} предоставил Вам "
                               f"{'админские права' if is_administrator else 'права пользователя'}.")
    else:
        await bot.send_message(user_id,
                               f"Сожалею, но Ваш запрос был отклонен администратором {callback.from_user.full_name}")
    await callback.answer()


async def get_users(resource_ip=None) -> tuple or list:
    users_list = []
    all_users = await check_users_exist()
    if not resource_ip:
        users_list = all_users.copy()
        return users_list
    else:
        users_id = await get_resource_users(resource_ip)
        for user in all_users:
            if user[0] not in users_id:
                users_list.append(user)
        return users_list, users_id


async def add_user(callback: types.CallbackQuery, state: FSMContext) -> None:
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
                                              reply_markup=choose_users_kb(data['users_list']))
                break
    await callback.answer()


async def exit_func(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()
    await callback.answer()
    await state.finish()


async def get_resources_list(user_id: int) -> list:
    resources_list = await get_resources()
    for resource in resources_list.copy():
        if str(user_id) not in ast.literal_eval(resource[3]):
            resources_list.remove(resource)
    return resources_list
