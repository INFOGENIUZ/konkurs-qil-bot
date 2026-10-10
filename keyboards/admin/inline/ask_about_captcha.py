from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .cancel_action import bt_admin_cancel_action


bt_admin_add_captcha_for_give = InlineKeyboardButton('✅ Ha, yoqilsin', callback_data='admin_add_captcha_for_give', style='success')
bt_admin_not_add_captcha_for_give = InlineKeyboardButton('❌ Kerak emas', callback_data='admin_not_add_captcha_for_give', style='danger')

kb_admin_add_captcha_for_give = InlineKeyboardMarkup().add(
    bt_admin_add_captcha_for_give, bt_admin_not_add_captcha_for_give
).add(
    bt_admin_cancel_action
)
