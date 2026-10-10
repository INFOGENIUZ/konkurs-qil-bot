from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


bt_admin_add_give_photo = InlineKeyboardButton('✅ Ha (Rasm/Video)', callback_data='admin_add_give_photo', style='success')
bt_admin_not_add_give_photo = InlineKeyboardButton('❌ Kerak emas', callback_data='admin_not_add_give_photo', style='danger')

kb_admin_add_give_photo = InlineKeyboardMarkup().add(bt_admin_add_give_photo, bt_admin_not_add_give_photo)