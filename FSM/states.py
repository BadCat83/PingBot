from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    unapproved = State()
    approved = State()
