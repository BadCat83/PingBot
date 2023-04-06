from aiogram import types, Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from DB.sqlite import create_user
from FSM.states import UserStates


def return_user_data(user: types.User) -> tuple:
    return (user.id, user.username, user.full_name)


async def create_new_user(
        callback: types.CallbackQuery,
        bot: Bot,
        state: FSMContext = None,
        dp: Dispatcher = None,
        is_adminstrator=False
) -> None:
    user_id = callback.message.text.split('"')[1]
    if state:
        data = await state.storage.get_data(chat=user_id, user=user_id)
        data['user'].is_administrator = is_adminstrator
        await create_user(data['user'])
        await callback.message.answer(
            f"Пользователь {data['user'].user_name} добавлен в качестве "
            f"{'пользователя' if not is_adminstrator else 'администратора'} системы.")
        state = dp.current_state(chat=user_id, user=user_id)
        await state.set_state(UserStates.approved)
    else:
        user_name = (await bot.get_chat_member(chat_id=user_id, user_id=int(user_id))).user.full_name
        await callback.message.answer(f'Вы отклонили запрос пользователя {user_name}')
    await callback.message.delete()
    if state:
        await bot.send_message(user_id,
                               f"Администратор {callback.from_user.full_name} предоставил Вам "
                               f"{'админские права' if is_adminstrator else 'права пользователя'}.")
    else:
        await bot.send_message(user_id,
                               f"Сожалею, но Ваш запрос был отклонен администратором {callback.from_user.full_name}")
    await callback.answer()