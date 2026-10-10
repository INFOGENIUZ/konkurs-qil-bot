from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified

from app import dp
from keyboards import kb_admin_menu, kb_main_menu
from .admin.functions_for_active_gives.handle_new_members_from_button_giveaways import (
    manage_new_members_from_button_gives,
    send_participant_card,
)
from .admin.functions_for_active_gives.check_channels_subscriptions import (
    get_channels_subscription_details,
    check_channels_subscriptions,
)
from database import TemporaryUsers, GiveAwayStatistic, GiveAway
from config import start_text


def build_subscription_checklist(
    give_name: str,
    give_callback_value: str,
    details: list[dict]
) -> tuple[str, types.InlineKeyboardMarkup]:
    """Shart kanallar ro‘yxati (1-shart, 2-shart) va qayta tekshirish tugmasini hosil qilish"""
    text = (
        "⚠️ <b>ISHTIROK ETISH TALABI</b>\n\n"
        f"🎉 «<b>{give_name}</b>» konkursida qatnashish uchun barcha homiy kanallarga a’zo bo‘lishingiz zarur!\n\n"
        "📋 <b>Shartlar holati:</b>\n"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)

    for idx, ch in enumerate(details, 1):
        ch_name = ch.get('name', 'Kanal')
        is_sub = ch.get('is_subscribed', False)
        status_line = "✅ A’zo bo‘lingan" if is_sub else "❌ A’zo bo‘linmagan!"
        text += f"  {idx}️⃣ <b>{idx}-shart:</b> «{ch_name}»\n      └──► {status_line}\n"

        if not is_sub and ch.get('link'):
            btn_title = f"{idx}️⃣ {idx}-shart: {ch_name[:18]}"
            markup.add(
                types.InlineKeyboardButton(
                    text=f"📢 {btn_title} »",
                    url=ch['link']
                )
            )

    text += (
        "\n\n👇 <i>Yuqoridagi kanallarga obuna bo‘ling va quyidagi tugma orqali tekshiring:</i>"
    )

    markup.add(
        types.InlineKeyboardButton(
            text="🔄 Qayta tekshirish",
            callback_data=f"check_sub_{give_callback_value}"
        )
    )

    return text, markup


@dp.message_handler(
    commands=['start'],
    state='*'
)
async def process_start(jam: types.Message, state: FSMContext):
    await state.finish()

    if ' ' in jam.text:
        give_callback_value = jam.text.split(' ')[1]

        if '=watchresult' in give_callback_value:
            give_callback_value = give_callback_value.split('=')[0]

            await TemporaryUsers().add_user(
                callback_value=give_callback_value,
                new_member_id=jam.from_user.id,
                new_member_username=jam.from_user.username
            )

            await jam.answer(
                '💎 <b>NATIJALARNI KUZATISH</b>\n\n'
                '✅ <b>Siz konkurs natijalarini kuzatuvchilar safiga qo‘shildingiz!</b>\n\n'
                '⏳ Konkurs yakunlanishi bilan g‘oliblar ushbu botda va kanalda e’lon qilinadi.',
            )

        elif '=getresults' in give_callback_value:
            give_callback_value = give_callback_value.split('=')[0]

            winners_data = await GiveAwayStatistic().filter(
                giveaway_callback_value=give_callback_value
            ).all().values('winners')

            text = (
                "🏆 <b>KONKURS NATIJALARI</b>\n\n"
                "🎉 <b>G‘oliblar ro‘yxati:</b>\n\n"
            )
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            for winners_users in winners_data:
                winners_users = winners_users['winners'] if winners_users['winners'] else []

                for i in range(len(winners_users)):
                    user_info = winners_users[i]
                    place = user_info['place']
                    medal = medals.get(place, "🎖")
                    text += f"  {medal} <b>{place}-o‘rin:</b> @{user_info['username']}\n"

            text += "\n\n👏 Barcha g‘oliblarni chin dildan tabriklaymiz!"
            await jam.answer(text=text)

        else:
            give_data = await GiveAway().get_give_data_for_owner(callback_value=give_callback_value)
            if not give_data:
                await jam.answer(
                    '⚠️ <b>Kechirasiz, ushbu konkurs topilmadi yoki yakunlangan!</b>'
                )
                return

            give_name = give_data[0].get('name', 'Konkurs')

            # Allaqachon a'zo bo'lganmi?
            is_already = await GiveAwayStatistic().exists_member(
                giveaway_callback_value=give_callback_value,
                member_username=jam.from_user.username,
                member_id=jam.from_user.id
            )
            if is_already:
                await send_participant_card(
                    user=jam.from_user,
                    give_callback_value=give_callback_value,
                    is_already=True
                )
                return

            details = await get_channels_subscription_details(
                give_callback_value=give_callback_value,
                user_id=jam.from_user.id
            )

            all_sub = all(ch['is_subscribed'] for ch in details) if details else True

            if all_sub:
                await manage_new_members_from_button_gives(
                    jam=jam,
                    state=state,
                    give_callback_value=give_callback_value,
                    user=jam.from_user
                )
            else:
                text, markup = build_subscription_checklist(
                    give_name=give_name,
                    give_callback_value=give_callback_value,
                    details=details
                )
                await jam.answer(text=text, reply_markup=markup)

    else:
        await state.finish()
        await jam.answer(
            start_text,
            reply_markup=kb_main_menu
        )
        await jam.answer(
            '🎛 <b>Tezkor boshqaruv menyusi:</b>',
            reply_markup=kb_admin_menu
        )


@dp.callback_query_handler(lambda c: c.data.startswith('check_sub_'), state='*')
async def process_recheck_subscription(call: types.CallbackQuery, state: FSMContext):
    give_callback_value = call.data.replace('check_sub_', '')

    give_data = await GiveAway().get_give_data_for_owner(callback_value=give_callback_value)
    if not give_data:
        await call.answer("⚠️ Konkurs topilmadi yoki yakunlangan!", show_alert=True)
        return

    # Allaqachon a'zo bo'lganmi?
    is_already = await GiveAwayStatistic().exists_member(
        giveaway_callback_value=give_callback_value,
        member_username=call.from_user.username,
        member_id=call.from_user.id
    )
    if is_already:
        await call.answer("✅ Siz allaqachon konkurs ishtirokchisisiz!", show_alert=False)
        try:
            await call.message.delete()
        except Exception:
            pass
        await send_participant_card(
            user=call.from_user,
            give_callback_value=give_callback_value,
            is_already=True
        )
        return

    # Obunani tekshirish
    details = await get_channels_subscription_details(
        give_callback_value=give_callback_value,
        user_id=call.from_user.id
    )

    missing = [ch for ch in details if not ch['is_subscribed']]
    if not missing:
        await call.answer("🎉 Barcha shartlar muvaffaqiyatli bajarildi!", show_alert=False)
        try:
            await call.message.delete()
        except Exception:
            pass
        await manage_new_members_from_button_gives(
            jam=call,
            give_callback_value=give_callback_value,
            state=state,
            user=call.from_user
        )
    else:
        await call.answer(
            f"⚠️ Hali {len(missing)} ta homiy kanalga a’zo emassiz! Iltimos, barchasiga obuna bo‘ling.",
            show_alert=True
        )
        give_name = give_data[0].get('name', 'Konkurs')
        text, markup = build_subscription_checklist(
            give_name=give_name,
            give_callback_value=give_callback_value,
            details=details
        )
        try:
            await call.message.edit_text(text=text, reply_markup=markup)
        except MessageNotModified:
            pass
        except Exception:
            pass


@dp.message_handler(
    commands=['menu'],
    state='*'
)
async def process_menu(jam: types.Message, state: FSMContext):
    await state.finish()
    await jam.answer(
        start_text,
        reply_markup=kb_main_menu
    )
    await jam.answer(
        '🎛 <b>Tezkor boshqaruv menyusi:</b>',
        reply_markup=kb_admin_menu
    )


@dp.message_handler(
    commands=['help'],
    state='*'
)
async def process_help(jam: types.Message, state: FSMContext):
    await state.finish()
    await jam.answer(
        "ℹ️ <b>YORDAM VA FOYDALANISH QO‘LLANMASI</b>\n\n"
        "Ushbu bot Telegram kanallarida shaffof va avtomatlashtirilgan konkurslar (giveaway) o‘tkazish uchun xizmat qiladi.\n\n"
        "📌 <b>Asosiy buyruqlar:</b>\n"
        "• /start — Botni ishga tushirish va boshqaruv panelini ochish\n"
        "• /help — Botdan foydalanish bo‘yicha qo‘llanma\n\n"
        "🎁 <b>Konkurs tashkil qilish bosqichlari:</b>\n"
        "1️⃣ <b>Kanal ulash:</b> «📢 Kanallarni boshqarish» bo‘limiga kiring va kanalingiz havolasini yuboring (bot kanalda admin bo‘lishi shart);\n"
        "2️⃣ <b>Konkurs yaratish:</b> «🎁 Konkurs yaratish» tugmasini bosib, ishtirok formatini (tugma yoki izoh), matnini va tugash vaqtini belgilang;\n"
        "3️⃣ <b>Ishga tushirish:</b> «📋 Yaratilgan konkurslar» bo‘limidan konkursni tanlang va «🚀 Boshlash» orqali xohlagan kanalingizda e’lon qiling.\n\n"
        "⚡️ G‘oliblar belgilangan vaqtda bot tomonidan mutlaqo shaffof va tasodifiy tarzda aniqlanadi!",
        reply_markup=kb_main_menu
    )

