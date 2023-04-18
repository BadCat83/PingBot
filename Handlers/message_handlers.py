import ast

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from Config.config import User
from FSM.states import ResourceStates, EditResourceStates, AdminState, SubscribeState
import Keyboards.keyboards as kb
from Utils.formating import format_resources_list
from Utils.func import get_users, get_resources_list, show_subscribes
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
        await msg.delete()
        await AdminState.admin.set()
    elif not bool(is_administrator := await db.check_user(msg.from_user.id)):
        await msg.answer("Пожалуйста, подождите пока ваш профиль одобрит администратор.")
        await msg.delete()
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
        await msg.answer(f"Вы авторизованы в системе в качестве"
                         f" {'администратора' if is_administrator[0] else 'пользователя'}, можете продолжать работу",
                         reply_markup=kb.admin_kb() if is_administrator[0] else kb.user_kb())
        await msg.delete()


async def help_cmd(msg: types.Message, state: FSMContext):
    is_admin = 'admin' in (await state.get_state())
    text = f"Данный бот позволяет пинговать заданные администратором ресурсы и слать оповещения подписавшимся" \
           f" на ресурс пользователям оповещения в случае недоступности ресурса.\n<b>/help</b> - Вывести помощь" \
           f" по командам бота.\n<b>/start</b> - Начать работу с ботом, первый пользователь начавший работу при " \
           f"пустой базе становится адимнистратором.\n" \
           f"{'<b>/add_resource</b> - Добавить ресурс.' if is_admin else '<b>/subscribe_to_resource</b> - Подписаться на ресурс.'}\n" \
           f"{'<b>/add_user_to_resource</b> - Добавить пользователя к мониторингу ресурса' if is_admin else ''}\n" \
           f"<b>/show_subscribe</b> - Показать подписки" \
           f"<b>/unsubscribe</b> - Отписаться"
    await msg.answer(text, parse_mode='HTML')
    await msg.delete()


async def cancel_cmd(msg: types.Message, state: FSMContext) -> None:
    await state.finish()
    await AdminState.admin.set()
    await msg.answer("Вы отменили действие", reply_markup=kb.admin_kb())
    await msg.delete()


async def add_user_to_resource(msg: types.Message) -> None:
    await msg.answer("Выберите ресурс к которому необходимо добавить пользователя",
                     reply_markup=kb.add_users_to_res_kb(await db.get_resources()), )
    await msg.delete()
    await EditResourceStates.add_user.set()


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
                     reply_markup=kb.choose_users_kb(data['users_list']))
    await ResourceStates.next()


async def subscribe(msg: types.Message, state: FSMContext) -> None:
    resources = await db.get_resources()
    for resource in resources.copy():
        if resource[3][1:-1] and str(msg.from_user.id) in resource[3]:
            resources.remove(resource)
    if not resources:
        await msg.answer("Нет ресурсов на которые Вы не подписаны!", reply_markup=kb.user_kb())
    else:
        async with state.proxy() as data:
            data['resources'] = []
            data['resources_list'] = resources
        await msg.answer("Выберите ресурс на который хотите подписаться",
                         reply_markup=kb.add_users_to_res_kb(resources, first_time_use=True), )
        await SubscribeState.subscribe.set()
    await msg.delete()


async def unsubscribe(msg: types.Message, state: FSMContext) -> None:
    resources_list = await get_resources_list(msg.from_user.id)
    is_admin = 'admin' in (await state.get_state())
    if resources_list:
        await msg.answer(f"От какого ресурса Вы хотите отписаться?:{format_resources_list(resources_list)}"
                         , parse_mode='HTML', reply_markup=kb.unsubscribe_kb(resources_list))
    else:
        await msg.answer("Нет подписок!", reply_markup=kb.admin_kb() if is_admin else kb.user_kb())
    await msg.delete()


async def show_subscribe(msg: types.Message, state: FSMContext) -> None:
    await show_subscribes(msg, state)
    # resources_list = await get_resources_list(msg.from_user.id)
    # is_admin = 'admin' in (await state.get_state())
    # if resources_list:
    #     await msg.answer(f"Вы подписаны на следующие ресурсы:{format_resources_list(resources_list)}"
    #                      , parse_mode='HTML', reply_markup=kb.admin_kb() if is_admin else kb.user_kb())
    # else:
    #     await msg.answer("Нет подписок!", reply_markup=kb.admin_kb() if is_admin else kb.user_kb())
    await msg.delete()


async def send_echo(msg: types.Message) -> None:
    await msg.answer(msg.text)


def register_message_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start', ], state='*')
    dp.register_message_handler(help_cmd, commands=['help', ], state=[AdminState.admin, AdminState.user])
    dp.register_message_handler(add_resource, commands=['add_resource', ], state=AdminState.admin)
    dp.register_message_handler(subscribe, commands=['subscribe', ], state=AdminState.user)
    dp.register_message_handler(show_subscribe, commands=['show_subscribe', ],
                                state=[AdminState.admin, AdminState.user])
    dp.register_message_handler(unsubscribe, commands=['unsubscribe', ],
                                state=[AdminState.admin, AdminState.user])
    dp.register_message_handler(add_user_to_resource, commands=['add_user_to_resource', ], state=AdminState.admin)
    dp.register_message_handler(cancel_cmd, commands=['cancel'], state='*')
    dp.register_message_handler(add_resource_name, state=ResourceStates.resource_name)
    dp.register_message_handler(add_ip_address, state=ResourceStates.ip_address)
    dp.register_message_handler(add_describe, state=ResourceStates.describe)
    dp.register_message_handler(send_echo, state=[AdminState.admin, AdminState.user])
