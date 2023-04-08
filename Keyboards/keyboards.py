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


def admin_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton('/add_resource')]], resize_keyboard=True)


def user_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton('/choose_resources')]], resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton('/cancel')]], resize_keyboard=True)
