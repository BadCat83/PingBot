from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    unapproved = State()
    approved = State()


class AdminState(StatesGroup):
    admin = State()
    user = State()


class ResourceStates(StatesGroup):
    resource_name = State()
    ip_address = State()
    describe = State()
    add_users = State()


class EditResourceStates(StatesGroup):
    add_user = State()
    finish = State()
