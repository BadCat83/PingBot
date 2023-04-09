from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from Config.config import User, Resource
from FSM.states import UserStates, ResourceStates
import Keyboards.keyboards as kb
from Utils.func import get_users
from init_bot import bot, db
import ipaddress


async def start_cmd(msg: types.Message, state: FSMContext) -> None:
    if not await db.check_users_exist():
        admin = User(user_id=msg.from_user.id,
                     nick=msg.from_user.username,
                     user_name=msg.from_user.full_name,
                     is_administrator=True)
        await db.create_user(admin)
        await msg.answer("Теперь Вы являетесь основным администратором данного бота", reply_markup=kb.admin_kb())
    elif not bool(is_administrator := await db.check_user(msg.from_user.id)):
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
                                   reply_markup=kb.user_add_kb())
    else:
        await msg.answer("Вы авторизованы в системе, можете продолжать работу",
                         reply_markup=kb.admin_kb() if is_administrator else kb.user_kb())
    await msg.delete()


async def help_cmd(msg: types.Message):
    is_admin = await db.check_user(msg.from_user.id)
    text = f"Данный бот позволяет пинговать заданные администратором ресурсы и слать оповещения подписавшимся" \
           f" на ресурс пользователям оповещения в случае недоступности ресурса.\n<b>/help</b> - Вывести помощь" \
           f" по командам бота.\n<b>/start</b> - Начать работу с ботом, первый пользователь начавший работу при " \
           f"пустой базе становится адимнистратором.\n{'<b>/add_resource</b> - Добавить ресурс.' if is_admin else ''}"
    await msg.answer(text, parse_mode='HTML')
    await msg.delete()


async def cancel_cmd(msg: types.Message, state: FSMContext) -> None:
    await state.finish()
    await msg.answer("Вы отменили действие", reply_markup=kb.admin_kb())
    await msg.delete()


async def add_resource(msg: types.Message) -> None:
    await msg.answer("Добавьте имя нового ресурса", reply_markup=kb.cancel_kb())
    await msg.delete()
    await ResourceStates.resource_name.set()


async def add_resource_name(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['resource_name'] = msg.text
        await msg.reply(f"Какой IP адрес у {data['resource_name']}?")
    await ResourceStates.next()


async def add_ip_address(msg: types.Message, state: FSMContext) -> None:
    try:
        ip = ipaddress.ip_address(msg.text)
    except ValueError:
        await msg.reply(f"Некорректный ip адрес!")
    else:
        async with state.proxy() as data:
            data['ip_address'] = ip
            await msg.reply(f"Добавьте описание ресурса {data['resource_name']}.")
        await ResourceStates.next()


async def add_describe(msg: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['describe'] = msg.text
        data['users_list'] = await get_users()
    await msg.answer("А теперь добавьте пользователей которым необходимо слать оповещение при недосутупности ресурса",
                     reply_markup=await kb.choose_users_kb(data['users_list']))
    await ResourceStates.next()


async def send_echo(msg: types.Message) -> None:
    await msg.answer(msg.text)


def register_message_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start', ])
    dp.register_message_handler(help_cmd, commands=['help', ])
    dp.register_message_handler(add_resource, commands=['add_resource', ])
    dp.register_message_handler(cancel_cmd, commands=['cancel'], state='*')
    dp.register_message_handler(add_resource_name, state=ResourceStates.resource_name)
    dp.register_message_handler(add_ip_address, state=ResourceStates.ip_address)
    dp.register_message_handler(add_describe, state=ResourceStates.describe)
    dp.register_message_handler(send_echo, state=UserStates.approved)
