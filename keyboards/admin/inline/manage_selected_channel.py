from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .cancel_action import bt_admin_cancel_action


bt_admin_add_group_for_channel = InlineKeyboardButton('👥 Guruh ulash', callback_data='admin_add_group', style='primary')
bt_admin_delete_channel = InlineKeyboardButton('🗑 Kanalni o‘chirish', callback_data='admin_delete_channel', style='danger')

kb_admin_manage_selected_channel = InlineKeyboardMarkup().add(
    bt_admin_add_group_for_channel
).add(
    bt_admin_delete_channel
).add(
    bt_admin_cancel_action
)
