from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


bt_admin_create_give = InlineKeyboardButton('🎁 Konkurs yaratish', callback_data='admin_gives', style='primary')
bt_admin_created_gives = InlineKeyboardButton('📋 Yaratilgan konkurslar', callback_data='admin_created_gives', style='primary')
bt_admin_started_gives = InlineKeyboardButton('🚀 Faol konkurslar', callback_data='admin_started_gives', style='success')

kb_admin_menu = InlineKeyboardMarkup().add(bt_admin_create_give, bt_admin_created_gives).add(bt_admin_started_gives)
