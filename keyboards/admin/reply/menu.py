from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Asosiy doimiy menyu (Reply Keyboard - Style background)
bt_reply_create_give = KeyboardButton('🎁 Konkurs yaratish', style='primary')
bt_reply_created_gives = KeyboardButton('📋 Yaratilgan konkurslar', style='primary')
bt_reply_active_gives = KeyboardButton('🚀 Faol konkurslar', style='success')
bt_reply_channels = KeyboardButton('📢 Kanallarni boshqarish', style='primary')
bt_reply_stats = KeyboardButton('📊 Umumiy statistika', style='primary')

kb_main_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2
).add(
    bt_reply_create_give
).row(
    bt_reply_created_gives,
    bt_reply_active_gives
).row(
    bt_reply_channels,
    bt_reply_stats
)


# Jarayonni bekor qilish uchun Reply tugma
bt_reply_cancel = KeyboardButton('❌ Bekor qilish', style='danger')
kb_cancel_reply = ReplyKeyboardMarkup(
    resize_keyboard=True
).add(bt_reply_cancel)
