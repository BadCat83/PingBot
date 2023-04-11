from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

users_cb = CallbackData('user', 'action')


def user_add_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton('Добавить в качестве пользователя',
                                               callback_data='add_as_user')],
                         [InlineKeyboardButton('Добавить в качестве администратора',
                                               callback_data='add_as_admin')],
                         [InlineKeyboardButton('Отклонить запрос', callback_data='cancel_query')]])


async def choose_users_kb(users_list: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{user[2]}", callback_data=f'add_user_{user[0]}')] for user in users_list
    ])
    return kb.add(InlineKeyboardButton("Сохранить...", callback_data='save'))


async def add_users_to_res_kb(resources_list: list, first_time_use: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=3)
    if resources_list:
        for resource in resources_list:
            kb.insert(
                InlineKeyboardButton(f"{resource[1]}", callback_data=f'{resource[0]},{resource[1]},{resource[3]}'))
    if not first_time_use:
        kb.add(InlineKeyboardButton("Сохранить", callback_data='save_subscribe'))
    return kb.add(InlineKeyboardButton("Выйти", callback_data='exit'))


def admin_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('/add_resource')],
        [KeyboardButton('/add_user_to_resource')],
        [KeyboardButton('/show_subscribe')]
    ], resize_keyboard=True, one_time_keyboard=True)


def user_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton('/choose_resources')],
                                         [KeyboardButton('/show_subscribe')]],
                               resize_keyboard=True,
                               one_time_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton('/cancel')]], resize_keyboard=True)
