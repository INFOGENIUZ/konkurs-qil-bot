from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .cancel_action import bt_admin_cancel_action


bt_admin_start_give = InlineKeyboardButton('🚀 Boshlash', callback_data='admin_start_give', style='success')
bt_admin_delete_give = InlineKeyboardButton('🗑 O‘chirish', callback_data='admin_delete_give', style='danger')
bt_admin_manage_channels = InlineKeyboardButton('📢 Kanallar', callback_data='admin_manage_channels', style='primary')
bt_admin_change_over_date = InlineKeyboardButton('⏱ Tugash vaqti', callback_data='admin_change_over_date', style='primary')

kb_admin_manage_created_gives = InlineKeyboardMarkup().add(
    bt_admin_start_give, bt_admin_delete_give
).add(
    bt_admin_manage_channels
).add(
    bt_admin_change_over_date
).add(
    bt_admin_cancel_action
)
