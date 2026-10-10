from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified

from app import bot, dp
from keyboards import kb_admin_menu, kb_main_menu
from keyboards.admin.inline.owner_menu import kb_owner_panel
from config import start_text, OWNERS
from database import TemporaryUsers, GiveAwayStatistic, GiveAway, BotUser, MandatoryChannel
from .admin.functions_for_active_gives.handle_new_members_from_button_giveaways import (
    manage_new_members_from_button_gives,
    send_participant_card,
)
from .admin.functions_for_active_gives.check_channels_subscriptions import (
    get_channels_subscription_details,
    check_channels_subscriptions,
)


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


async def check_mandatory_subs(user_id: int) -> tuple[bool, list[dict]]:
    """Tizim miqyosidagi homiy kanallarga (OP) obunani tekshirish"""
    channels = await MandatoryChannel.get_active_channels()
    if not channels:
        return True, []

    missing = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch['channel_id'], user_id=user_id)
            if member.status in ['left', 'kicked']:
                missing.append(ch)
        except Exception:
            pass
    return len(missing) == 0, missing


def build_mandatory_op_markup(missing_channels: list[dict], ref_param: str = "") -> types.InlineKeyboardMarkup:
    """Majburiy homiy kanallar (OP) uchun havola tugmalari va tekshirish tugmasi"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    for idx, ch in enumerate(missing_channels, 1):
        url = ch.get('invite_link') or "https://t.me"
        markup.add(
            types.InlineKeyboardButton(
                text=f"📢 {idx}. {ch['name'][:25]} »",
                url=url
            )
        )
    cb_data = f"chk_op_{ref_param}" if ref_param else "chk_op_main"
    markup.add(
        types.InlineKeyboardButton(
            text="🔄 Obunani tekshirish",
            callback_data=cb_data
        )
    )
    return markup


async def handle_giveaway_start_payload(
    user: types.User,
    chat_id: int,
    give_callback_value: str,
    state: FSMContext,
    reply_message: types.Message = None
):
    """Start payloadi (konkursga qatnashish, natija kuzatish) mantig'i"""
    if '=watchresult' in give_callback_value:
        give_callback_value = give_callback_value.split('=')[0]

        await TemporaryUsers().add_user(
            callback_value=give_callback_value,
            new_member_id=user.id,
            new_member_username=user.username
        )

        msg = (
            '💎 <b>NATIJALARNI KUZATISH</b>\n\n'
            '✅ <b>Siz konkurs natijalarini kuzatuvchilar safiga qo‘shildingiz!</b>\n\n'
            '⏳ Konkurs yakunlanishi bilan g‘oliblar ushbu botda va kanalda e’lon qilinadi.'
        )
        if reply_message:
            await reply_message.answer(msg)
        else:
            await bot.send_message(chat_id, msg)

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
        if reply_message:
            await reply_message.answer(text)
        else:
            await bot.send_message(chat_id, text)

    else:
        give_data = await GiveAway().get_give_data_for_owner(callback_value=give_callback_value)
        if not give_data:
            msg = '⚠️ <b>Kechirasiz, ushbu konkurs topilmadi yoki yakunlangan!</b>'
            if reply_message:
                await reply_message.answer(msg)
            else:
                await bot.send_message(chat_id, msg)
            return

        give_name = give_data[0].get('name', 'Konkurs')

        # Allaqachon a'zo bo'lganmi?
        is_already = await GiveAwayStatistic().exists_member(
            giveaway_callback_value=give_callback_value,
            member_username=user.username,
            member_id=user.id
        )
        if is_already:
            await send_participant_card(
                user=user,
                give_callback_value=give_callback_value,
                is_already=True
            )
            return

        details = await get_channels_subscription_details(
            give_callback_value=give_callback_value,
            user_id=user.id
        )

        all_sub = all(ch['is_subscribed'] for ch in details) if details else True

        if all_sub:
            await manage_new_members_from_button_gives(
                jam=reply_message,
                state=state,
                give_callback_value=give_callback_value,
                user=user
            )
        else:
            text, markup = build_subscription_checklist(
                give_name=give_name,
                give_callback_value=give_callback_value,
                details=details
            )
            if reply_message:
                await reply_message.answer(text=text, reply_markup=markup)
            else:
                await bot.send_message(chat_id, text=text, reply_markup=markup)


@dp.message_handler(
    commands=['start'],
    state='*'
)
async def process_start(jam: types.Message, state: FSMContext):
    await state.finish()

    # Bot foydalanuvchilarini bazada ro'yxatga olamiz / yangilaymiz
    try:
        await BotUser.add_or_update(
            user_id=jam.from_user.id,
            username=jam.from_user.username,
            first_name=jam.from_user.first_name
        )
    except Exception as e:
        import logging
        logging.error(f"BotUser add error: {e}")

    # Homiy kanallarga majburiy obuna (OP) tekshiruvi (Bot egasi uchun shart emas)
    if jam.from_user.id not in OWNERS:
        is_sub, missing = await check_mandatory_subs(jam.from_user.id)
        if not is_sub:
            payload = jam.text.split(' ')[1] if ' ' in jam.text else "main"
            markup = build_mandatory_op_markup(missing, ref_param=payload)
            await jam.answer(
                "🔐 <b>BOTDAN FOYDALANISH UCHUN HOMIY KANALLARGA OBUNA BO‘LING</b>\n\n"
                "Assalomu alaykum! Bot xizmatlaridan foydalanish uchun quyidagi rasmiy kanallarga a’zo bo‘lishingiz zarur.\n\n"
                "Obuna bo‘lgach, «🔄 Obunani tekshirish» tugmasini bosing:",
                reply_markup=markup
            )
            return

    if ' ' in jam.text:
        give_callback_value = jam.text.split(' ')[1]
        await handle_giveaway_start_payload(
            user=jam.from_user,
            chat_id=jam.chat.id,
            give_callback_value=give_callback_value,
            state=state,
            reply_message=jam
        )
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
        if jam.from_user.id in OWNERS:
            await jam.answer(
                "👑 <b>Xush kelibsiz, Bot Egasi!</b>\n\n"
                "Global statistika, xabar tarqatish, homiy kanallar va barcha konkurslarni boshqarish uchun "
                "boshqaruv panelini ochishingiz mumkin:\n"
                "👉 /owner yoki quyidagi tugma orqali:",
                reply_markup=kb_owner_panel
            )


@dp.callback_query_handler(lambda c: c.data.startswith('chk_op_'), state='*')
async def process_check_mandatory_op(call: types.CallbackQuery, state: FSMContext):
    ref_param = call.data.replace('chk_op_', '')

    if call.from_user.id not in OWNERS:
        is_sub, missing = await check_mandatory_subs(call.from_user.id)
        if not is_sub:
            await call.answer(
                f"⚠️ Hali {len(missing)} ta homiy kanalga a’zo bo‘lmadingiz! Iltimos, barchasiga obuna bo‘ling.",
                show_alert=True
            )
            markup = build_mandatory_op_markup(missing, ref_param=ref_param)
            try:
                await call.message.edit_reply_markup(reply_markup=markup)
            except Exception:
                pass
            return

    await call.answer("✅ Rahmat! Homiy kanallarga obuna tasdiqlandi.", show_alert=False)
    try:
        await call.message.delete()
    except Exception:
        pass

    if ref_param and ref_param != 'main':
        await handle_giveaway_start_payload(
            user=call.from_user,
            chat_id=call.message.chat.id,
            give_callback_value=ref_param,
            state=state,
            reply_message=None
        )
    else:
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=start_text,
            reply_markup=kb_main_menu
        )
        await bot.send_message(
            chat_id=call.message.chat.id,
            text='🎛 <b>Tezkor boshqaruv menyusi:</b>',
            reply_markup=kb_admin_menu
        )
        if call.from_user.id in OWNERS:
            await bot.send_message(
                chat_id=call.message.chat.id,
                text="👑 <b>Xush kelibsiz, Bot Egasi!</b>\n\n"
                     "Global statistika, xabar tarqatish, homiy kanallar va barcha konkurslarni boshqarish uchun "
                     "boshqaruv panelini ochishingiz mumkin:\n"
                     "👉 /owner yoki quyidagi tugma orqali:",
                reply_markup=kb_owner_panel
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
    if jam.from_user.id in OWNERS:
        await jam.answer(
            "👑 <b>Bot Egasi Boshqaruv Paneli:</b> /owner",
            reply_markup=kb_owner_panel
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
        "• /help — Botdan foydalanish bo‘yicha qo‘llanma\n"
        "• /menu — Asosiy menyuni qayta ochish\n\n"
        "🎁 <b>Konkurs tashkil qilish bosqichlari:</b>\n"
        "1️⃣ <b>Kanal ulash:</b> «📢 Kanallarni boshqarish» bo‘limiga kiring va kanalingiz havolasini yuboring (bot kanalda admin bo‘lishi shart);\n"
        "2️⃣ <b>Konkurs yaratish:</b> «🎁 Konkurs yaratish» tugmasini bosib, ishtirok formatini (tugma yoki izoh), matnini va tugash vaqtini belgilang;\n"
        "3️⃣ <b>Ishga tushirish:</b> «📋 Yaratilgan konkurslar» bo‘limidan konkursni tanlang va «🚀 Boshlash» orqali xohlagan kanalingizda e’lon qiling.\n\n"
        "⚡️ G‘oliblar belgilangan vaqtda bot tomonidan mutlaqo shaffof va tasodifiy tarzda aniqlanadi!",
        reply_markup=kb_main_menu
    )
