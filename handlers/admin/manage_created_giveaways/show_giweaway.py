from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from keyboards import *
from database import GiveAway
from states import CreatedGivesStates


@dp.callback_query_handler(
    text=bt_admin_created_gives.callback_data,
    state='*'
)
async def show_created_gives(jam: types.CallbackQuery):
    markup = await GiveAway().get_keyboard_of_created_gives(
        user_id=jam.from_user.id
    )

    if markup:
        markup.add(bt_admin_cancel_action)

        await jam.message.edit_text(
            '📋 <b>YARATILGAN KONKURSLAR</b>\n\n'
            'Ko‘rish, sozlash yoki boshlash uchun kerakli konkursni tanlang:',
            reply_markup=markup
        )
        await CreatedGivesStates.select_give.set()

    else:
        await jam.answer('⚠️ Sizda hali ishga tushirilmagan konkurslar mavjud emas!')




@dp.callback_query_handler(
    lambda c: c.data != bt_admin_cancel_action.callback_data,
    state=CreatedGivesStates.select_give,
)
async def show_selected_give(
    jam: types.CallbackQuery,
    state: FSMContext,
    give_callback_value: str = False
):
    await CreatedGivesStates.manage_selected_give.set()

    if not give_callback_value:
        give_callback_value = jam.data
    await state.update_data(give_callback_value=give_callback_value)

    give_data = await GiveAway().get_give_data(
        user_id=jam.from_user.id,
        callback_value=give_callback_value
    )

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
            f"🎁 <b>KONKURS MA’LUMOTLARI</b>\n\n"
            f"📌 <b>Nomi:</b> <code>{give['name']}</code>\n"
            f"⚙️ <b>Holati:</b> 🟡 <i>Ishga tushirishga tayyor</i>\n"
            f"🎯 <b>Formati:</b> <code>{type_str}</code>\n\n"
            f"📝 <b>Konkurs matni:</b>\n"
            f"{give['text']}\n\n"
            f"📊 <b>Sozlamalar va shartlar:</b>\n"
            f"  🏆 <b>G‘oliblar soni:</b> <code>{give['winners_count']} nafar</code>\n"
            f"  ⏳ <b>Yakunlanish vaqti:</b> <code>{date_str}</code>\n"
            f"  🤖 <b>Kaptcha himoyasi:</b> {captcha_str}\n"
            f"  📎 <b>Media fayl:</b> {media_str}\n\n"
            f"💡 <i>Konkursni boshlash uchun quyidagi «🚀 Boshlash» tugmasini bosing yoki kanallarni sozlang:</i>"
        )

    await jam.message.edit_text(
        message_text,
        reply_markup=kb_admin_manage_created_gives
    )
