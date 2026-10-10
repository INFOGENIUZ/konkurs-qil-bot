from aiogram import types
from aiogram.dispatcher import FSMContext
from app import dp
from database import GiveAway, GiveAwayStatistic
from keyboards import *
from states import ActiveGivesStates


@dp.callback_query_handler(
    lambda c: c.data != bt_admin_cancel_action.callback_data,
    state=ActiveGivesStates.select_give,
)
async def show_active_selected_give(
    jam: types.CallbackQuery,
    state: FSMContext,
    give_callback_value: str = False
):

    if not give_callback_value:
        give_callback_value = jam.data
    await state.update_data(give_callback_value=give_callback_value)

    give_data = await GiveAway().get_give_data(
        user_id=jam.from_user.id,
        callback_value=give_callback_value
    )

    stat_info = await GiveAwayStatistic().get_statistic(
        giveaway_callback_value=give_callback_value
    )
    members_count = stat_info.count_members_summary if stat_info else 0

    message_text = ''
    for give in give_data:
        await state.update_data(type_of_give=give['type'])
        date_str = give['over_date'].strftime('%d.%m.%Y %H:%M') if hasattr(give['over_date'], 'strftime') else str(give['over_date'])

        type_str = '💬 Izohlar orqali' if give['type'] == 'comments' else '🔘 Tugma orqali'
        captcha_str = '🟢 Yoqilgan (himoyalangan)' if give['captcha'] else '⚪️ O‘chirilgan'

        if give.get('photo_id'):
            media_str = '🖼 Rasm biriktirilgan'
        elif give.get('video_id'):
            media_str = '🎬 Video biriktirilgan'
        else:
            media_str = '❌ Yo‘q'

        message_text = (
            f"🚀 <b>FAOL KONKURS KARTASI</b>\n\n"
            f"📌 <b>Nomi:</b> <code>{give['name']}</code>\n"
            f"🟢 <b>Holati:</b> <b>FAOL (Davom etmoqda)</b>\n"
            f"🎯 <b>Formati:</b> <code>{type_str}</code>\n\n"
            f"📝 <b>Konkurs matni:</b>\n"
            f"{give['text']}\n\n"
            f"📊 <b>Jonli ko‘rsatkichlar:</b>\n"
            f"  👥 <b>Hozirgi ishtirokchilar:</b> <code>{members_count} nafar</code>\n"
            f"  🏆 <b>G‘oliblar soni:</b> <code>{give['winners_count']} nafar</code>\n"
            f"  ⏳ <b>Yakunlanish vaqti:</b> <code>{date_str}</code>\n"
            f"  🤖 <b>Kaptcha himoyasi:</b> {captcha_str}\n"
            f"  📎 <b>Media fayl:</b> {media_str}\n\n"
            f"💡 <i>Quyidagi tugmalar orqali batafsil statistikani ko‘rishingiz yoki konkursni to‘xtatishingiz mumkin:</i>"
        )

    await jam.message.edit_text(
        message_text,
        reply_markup=kb_admin_active_gives
    )
    await ActiveGivesStates.manage_selected_give.set()
