from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

users_cb = CallbackData('user', 'action')


def user_add_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton('Добавить в качестве пользователя',
                                               callback_data='add_as_user')],
                         [InlineKeyboardButton('Добавить в качестве администратора',
                                               callback_data='add_as_admin')],
                         [InlineKeyboardButton('Отклонить запрос', callback_data='cancel_query')]])
    return kb

def test_kb():
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton('/test')]])
    return kb