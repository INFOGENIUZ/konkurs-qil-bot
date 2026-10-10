from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app import dp
from config import OWNERS
from database import GiveAway, GiveAwayStatistic, TelegramChannel


@dp.callback_query_handler(text='owner_all_contests', state='*')
async def owner_show_active_contests(jam: types.CallbackQuery):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    gives = await GiveAway.filter(run_status=True).all().values('name', 'callback_value', 'owner_id', 'over_date')
    if not gives:
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton('🔙 Orqaga', callback_data='owner_back_to_panel')
        )
        await jam.message.edit_text(
            "ℹ️ <b>Hozirda tizimda faol (davom etayotgan) konkurslar mavjud emas.</b>",
            reply_markup=markup
        )
        return

    markup = InlineKeyboardMarkup()
    for g in gives:
        markup.add(
            InlineKeyboardButton(
                text=f"🚀 {g['name'][:22]}",
                callback_data=f"owner_view_give_{g['callback_value']}"
            )
        )
    markup.add(
        InlineKeyboardButton('🔙 Orqaga', callback_data='owner_back_to_panel')
    )

    await jam.message.edit_text(
        f"🌐 <b>TIZIMDAGI BARCHA FAOL KONKURSLAR ({len(gives)} ta):</b>\n\n"
        "Batafsil ko‘rish yoki majburiy to‘xtatish uchun konkursni tanlang:",
        reply_markup=markup
    )


@dp.callback_query_handler(lambda c: c.data.startswith('owner_view_give_'), state='*')
async def owner_view_single_contest(jam: types.CallbackQuery):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    give_cb = jam.data.replace('owner_view_give_', '')
    give = await GiveAway.filter(callback_value=give_cb).first()
    if not give:
        await jam.answer("⚠️ Konkurs topilmadi!", show_alert=True)
        return

    stat = await GiveAwayStatistic.filter(giveaway_callback_value=give_cb).first()
    members_count = len(stat.members) if stat and stat.members else 0

    date_str = give.over_date.strftime('%d.%m.%Y %H:%M') if hasattr(give.over_date, 'strftime') else str(give.over_date)

    text = (
        f"🎁 <b>KONKURS: {give.name}</b>\n\n"
        f"👤 <b>Yaratuvchi ID:</b> <code>{give.owner_id}</code>\n"
        f"👥 <b>Qatnashuvchilar:</b> <code>{members_count} nafar</code>\n"
        f"🏆 <b>G‘oliblar:</b> <code>{give.winners_count} nafar</code>\n"
        f"⏳ <b>Yakunlanish:</b> <code>{date_str}</code>\n"
        f"🛡 <b>Kaptcha:</b> {'Yoqilgan' if give.captcha else 'O‘chirilgan'}\n\n"
        f"📝 <b>Matn:</b>\n{give.text[:200]}..."
    )

    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            '⛔️ Majburiy to‘xtatish (Deaktivatsiya)',
            callback_data=f"owner_stop_give_{give_cb}"
        )
    ).add(
        InlineKeyboardButton('🔙 Ro‘yxatga qaytish', callback_data='owner_all_contests')
    )

    await jam.message.edit_text(text, reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data.startswith('owner_stop_give_'), state='*')
async def owner_force_stop_contest(jam: types.CallbackQuery):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    give_cb = jam.data.replace('owner_stop_give_', '')
    await GiveAway.filter(callback_value=give_cb).update(run_status=False)
    await jam.answer("✅ Konkurs majburiy to‘xtatildi!", show_alert=True)
    await owner_show_active_contests(jam)
