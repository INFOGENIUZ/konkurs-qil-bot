from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .cancel_action import bt_admin_cancel_action


bt_admin_show_statistic = InlineKeyboardButton('📊 Statistika', callback_data='admin_show_statistic', style='primary')
bt_admin_stop_give = InlineKeyboardButton('🛑 To‘xtatish', callback_data='admin_stop_give', style='danger')

kb_admin_active_gives = InlineKeyboardMarkup().add(
    bt_admin_show_statistic, bt_admin_stop_give
).add(
    bt_admin_cancel_action
)
