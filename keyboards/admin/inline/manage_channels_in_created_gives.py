from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .cancel_action import bt_admin_cancel_action


bt_admin_add_channel = InlineKeyboardButton('➕ Kanal qo‘shish', callback_data='admin_add_channel', style='success')
bt_admin_active_channels = InlineKeyboardButton('📢 Ulangan kanallar', callback_data='admin_active_channels', style='primary')

kb_admin_manage_channels = InlineKeyboardMarkup().add(
    bt_admin_add_channel
).add(
    bt_admin_active_channels
).add(
    bt_admin_cancel_action
)
