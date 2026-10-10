from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


bt_admin_cancel_action = InlineKeyboardButton('🔙 Bekor qilish', callback_data='admin_cancel_action', style='danger')
kb_admin_cancel_action = InlineKeyboardMarkup().add(bt_admin_cancel_action)
