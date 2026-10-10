from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .cancel_action import bt_admin_cancel_action


bt_admin_give_type_button = InlineKeyboardButton('🔘 Tugma orqali', callback_data='admin_give_type_button', style='success')
bt_admin_give_type_comments = InlineKeyboardButton('💬 Izohlar orqali', callback_data='admin_give_type_comments', style='primary')

kb_admin_select_type_of_give = InlineKeyboardMarkup().add(
    bt_admin_give_type_button, bt_admin_give_type_comments
).add(
    bt_admin_cancel_action
)
