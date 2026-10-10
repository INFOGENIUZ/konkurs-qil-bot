from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .cancel_action import bt_admin_cancel_action

bt_owner_active_gives = InlineKeyboardButton('🚀 Faol konkurslar', callback_data='owner_active_gives', style='success')
kb_owner_menu = InlineKeyboardMarkup().add(bt_owner_active_gives)

bt_owner_change_winners = InlineKeyboardButton('🎯 G‘oliblarni o‘zgartirish', callback_data='owner_change_winners', style='primary')
bt_owner_statistic = InlineKeyboardButton('📊 Statistika', callback_data='owner_show_statistic', style='primary')
kb_owner_manage_gives = InlineKeyboardMarkup().add(bt_owner_change_winners).add(bt_owner_statistic).add(
    bt_admin_cancel_action
)
