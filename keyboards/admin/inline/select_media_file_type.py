from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .cancel_action import bt_admin_cancel_action


bt_admin_add_media_photo = InlineKeyboardButton('🖼 Rasm', callback_data='admin_add_media_photo', style='primary')
bt_admin_add_media_video = InlineKeyboardButton('🎬 Video', callback_data='admin_add_media_video', style='primary')

kb_admin_select_media_file_type = InlineKeyboardMarkup().add(
    bt_admin_add_media_photo, bt_admin_add_media_video
).add(
    bt_admin_cancel_action
)
