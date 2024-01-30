from aiogram.dispatcher.filters.state import StatesGroup, State


class MyStates(StatesGroup):
    add_channel_check = State()
    add_channel_invite_check = State()
    send_message = State()
    add_movie = State()
    simple_send = State()
    default_space = State()
    add_admin_check = State()
    anyany = State()
