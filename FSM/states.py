from aiogram.dispatcher.filters.state import StatesGroup, State

"""Describes of all FSM"""


class UserStates(StatesGroup):
    """While users state is unapproved, they cannot interract with the bot"""
    unapproved = State()
    approved = State()


class AdminState(StatesGroup):
    """This state assigned to every approved users, depending on their rights"""
    admin = State()
    user = State()


class SubscribeState(StatesGroup):
    """The state is needed as a pointer for subscribe action"""
    subscribe = State()


class ResourceStates(StatesGroup):
    """This state as a pointer for creating resource"""
    resource_name = State()
    ip_address = State()
    describe = State()
    add_users = State()


class EditResourceStates(StatesGroup):
    """This state is needed for adding users to the resource"""
    add_user = State()
    finish = State()
