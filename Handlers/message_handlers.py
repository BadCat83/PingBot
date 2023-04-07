from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from Config.config import User
from FSM.states import UserStates
from Keyboards.keyboards import user_add_kb
from init_bot import bot, db


async def start_cmd(msg: types.Message, state: FSMContext) -> None:
    if not await db.check_users_exist():
        admin = User(user_id=msg.from_user.id,
                     nick=msg.from_user.username,
                     user_name=msg.from_user.full_name,
                     is_administrator=True)
        await db.create_user(admin)
        await msg.answer("Теперь Вы являетесь основным администратором данного бота")
        return
    await msg.answer("Пожалуйста, подождите пока ваш профиль одобрит администратор.")
    await msg.delete()
    await UserStates.unapproved.set()
    user = User(user_id=msg.from_user.id,
                nick=msg.from_user.username if msg.from_user.username else '',
                user_name=msg.from_user.full_name,
                is_administrator=False)
    async with state.proxy() as data:
        data['user'] = user
    ids, *other = await db.get_admin()
    for user_id in ids:
        await bot.send_message(user_id, f'Пользователь {msg.from_user.full_name} ждет Вашего утверждения.\n'
                                        f'ID пользователя: "{msg.from_user.id}"\n',
                               reply_markup=user_add_kb())


async def send_echo(msg: types.Message) -> None:
    await msg.answer(msg.text)


def register_message_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start', ])
    dp.register_message_handler(send_echo, state=UserStates.approved)
