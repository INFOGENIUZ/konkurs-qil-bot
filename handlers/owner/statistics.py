from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app import dp
from config import OWNERS
from database import GiveAway, TelegramChannel, GiveAwayStatistic, BotUser


@dp.callback_query_handler(text='owner_stats', state='*')
async def owner_show_global_stats(jam: types.CallbackQuery):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    # Foydalanuvchilar statistikasi
    total_users = await BotUser.get_total_count()
    today_users = await BotUser.get_today_count()

    # Konkurslar statistikasi
    active_gives = await GiveAway.filter(run_status=True).count()
    pending_gives = await GiveAway.filter(run_status=False).count()
    total_gives = active_gives + pending_gives

    # Ishtirokchilar statistikasi
    all_stats = await GiveAwayStatistic.all().values('members')
    total_participants = sum(len(item['members']) for item in all_stats if item.get('members'))

    # Kanallar statistikasi
    channels = await TelegramChannel.all().values('channel_id')
    distinct_channels_count = len({ch['channel_id'] for ch in channels})

    text = (
        "📊 <b>BOTNING GLOBAL STATISTIKASI</b>\n\n"
        "👥 <b>Foydalanuvchilar:</b>\n"
        f"  • Jami bot a’zolari: <code>{total_users} nafar</code>\n"
        f"  • Bugun qo‘shilganlar: <code>+{today_users} nafar</code>\n\n"
        "🎁 <b>Konkurslar ko‘rsatkichi:</b>\n"
        f"  • 🚀 Ayni damda faol: <code>{active_gives} ta</code>\n"
        f"  • 📋 Kutilayotgan: <code>{pending_gives} ta</code>\n"
        f"  • 📦 Jami yaratilgan: <code>{total_gives} ta</code>\n\n"
        "👥 <b>Qatnashuvchilar faolligi:</b>\n"
        f"  • Barcha konkurslarda jami: <code>{total_participants} nafar</code>\n\n"
        "📢 <b>Ulangan resurslar:</b>\n"
        f"  • Tizimdagi homiy kanallar: <code>{distinct_channels_count} ta</code>\n\n"
        "🕒 <i>Vaqt mintaqasi: Asia/Tashkent</i>"
    )

    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Orqaga', callback_data='owner_back_to_panel')
    )

    await jam.message.edit_text(text, reply_markup=markup)
