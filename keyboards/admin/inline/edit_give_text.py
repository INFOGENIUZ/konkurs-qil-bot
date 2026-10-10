from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


bt_admin_edit_give_text = InlineKeyboardButton('✏️ Matnni tahrirlash', callback_data='admin_edit_give_text', style='primary')
bt_admin_continue_create_give = InlineKeyboardButton('Davom etish ➡️', callback_data='admin_continue_create_give', style='success')

kb_admin_edit_give_text = InlineKeyboardMarkup().add(bt_admin_edit_give_text).add(bt_admin_continue_create_give)
