from aiogram.dispatcher.filters.state import State, StatesGroup


class OwnerStates(StatesGroup):
    main_menu = State()
    broadcast_get_message = State()
    broadcast_get_button = State()
    broadcast_confirm = State()
    add_mandatory_channel = State()
    select_global_contest = State()
