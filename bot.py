from aiogram import Bot, executor, Dispatcher, types
from aiogram.dispatcher import FSMContext

from Config.config import Settings, User
from FSM.states import UserStates
from Keyboards.keyboards import user_add_kb
from Middlewares.middlewares import ThrottlingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import DB.sqlite as db
from Utils.func import create_new_user

config = Settings()
storage = MemoryStorage()
bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)


async def on_startup(_):
    await db.db_start()


@dp.message_handler(commands='start')
async def start_cmd(msg: types.Message, state: FSMContext) -> None:
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
        # state = dp.current_state(chat=user_id, user=user_id)
        # await state.set_state(AddUserStates.unapproved)
        await bot.send_message(user_id, f'Пользователь {msg.from_user.full_name} ждет Вашего утверждения.\n'
                                        f'ID пользователя: "{msg.from_user.id}"\n',
                               reply_markup=user_add_kb())


@dp.message_handler(state=UserStates.approved)
async def send_echo(msg: types.Message) -> None:
    await msg.answer(msg.text)


@dp.callback_query_handler(text='add_as_user')
async def add_new_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    await create_new_user(callback, bot, state, dp)


@dp.callback_query_handler(text='add_as_admin')
async def add_new_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    await create_new_user(callback, bot, state, dp, is_adminstrator=True)


@dp.callback_query_handler(text='cancel_query')
async def cancel_query(callback: types.CallbackQuery):
    await create_new_user(callback, bot)


def bot_start() -> None:
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    bot_start()
