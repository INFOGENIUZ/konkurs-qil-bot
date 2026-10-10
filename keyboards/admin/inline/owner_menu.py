from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Asosiy egasi (Owner) paneli
kb_owner_panel = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton('📊 Global statistika', callback_data='owner_stats'),
    InlineKeyboardButton('📢 Xabar tarqatish', callback_data='owner_broadcast'),
).add(
    InlineKeyboardButton('🔐 Majburiy obuna (OP)', callback_data='owner_mandatory'),
    InlineKeyboardButton('🌐 Barcha konkurslar', callback_data='owner_all_contests'),
).add(
    InlineKeyboardButton('💾 Zaxira nusxa (Backup)', callback_data='owner_backup')
).add(
    InlineKeyboardButton('🔙 Asosiy menyu', callback_data='owner_back_to_main')
)

# Rassilka tugmasi uchun
kb_broadcast_buttons_opt = InlineKeyboardMarkup().add(
    InlineKeyboardButton('➕ Tugma qo‘shish', callback_data='broad_add_btn'),
    InlineKeyboardButton('⏩ Tugmasiz davom etish', callback_data='broad_skip_btn')
).add(
    InlineKeyboardButton('🔙 Bekor qilish', callback_data='broad_cancel')
)

# Rassilka tasdiqlash
kb_broadcast_confirm = InlineKeyboardMarkup().add(
    InlineKeyboardButton('🚀 Tarqatishni boshlash', callback_data='broad_confirm_send')
).add(
    InlineKeyboardButton('🔙 Bekor qilish', callback_data='broad_cancel')
)

# Majburiy obuna boshqaruvi
kb_mandatory_menu = InlineKeyboardMarkup().add(
    InlineKeyboardButton('➕ Homiy kanal qo‘shish', callback_data='mand_add')
).add(
    InlineKeyboardButton('📋 Ulangan homiy kanallar', callback_data='mand_list')
).add(
    InlineKeyboardButton('🔙 Orqaga', callback_data='owner_back_to_panel')
)
