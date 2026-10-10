from aiogram import types
from aiogram.dispatcher import FSMContext
from app import dp, bot
from keyboards import *
from states import CreatedGivesStates
from database import GiveAway, TelegramChannel, GiveAwayStatistic
from .functions_for_active_gives.check_channels_subscriptions import get_channel_invite_or_username


def build_simple_publish_keyboard(channel_data: list) -> InlineKeyboardMarkup:
    """Sodda va tezkor kanal tanlash klaviaturasi (1 bosishda boshlash)"""
    markup = InlineKeyboardMarkup()
    total = len(channel_data)

    if total == 1:
        markup.add(
            InlineKeyboardButton(
                text=f"📢 «{channel_data[0]['name'][:22]}» kanalida e’lon qilish",
                callback_data=f"pub_single_{channel_data[0]['channel_id']}",
                style="success"
            )
        )
        markup.add(
            InlineKeyboardButton(text="🔙 Bekor qilish", callback_data=bt_admin_cancel_action.callback_data, style="danger")
        )
        return markup

    # 1. Har bir kanal uchun alohida 1-klik tugma
    for ch in channel_data:
        ch_name = ch.get('name', 'Kanal')
        markup.add(
            InlineKeyboardButton(
                text=f"📢 «{ch_name[:24]}» kanalida",
                callback_data=f"pub_single_{ch['channel_id']}",
                style="primary"
            )
        )

    # 2. Barcha kanallarda bir bosishda e'lon qilish
    markup.add(
        InlineKeyboardButton(
            text=f"🌐 Barcha kanallarda e’lon qilish ({total} ta)",
            callback_data="pub_all",
            style="success"
        )
    )

    # 3. Agar 2 tadan ko'p kanal bo'lsa, bir nechtasini birgalikda tanlash imkoniyati
    if total > 2:
        markup.add(
            InlineKeyboardButton(
                text="🎯 Bir nechta kanalni birgalikda tanlash",
                callback_data="pub_multi_mode",
                style="primary"
            )
        )

    # 4. Bekor qilish
    markup.add(
        InlineKeyboardButton(text="🔙 Bekor qilish", callback_data=bt_admin_cancel_action.callback_data, style="danger")
    )
    return markup


def build_multi_publish_keyboard(channel_data: list, selected_ids: set) -> InlineKeyboardMarkup:
    """Bir nechta kanalni belgilash rejimi uchun klaviatura"""
    markup = InlineKeyboardMarkup()

    for ch in channel_data:
        is_sel = ch['channel_id'] in selected_ids
        icon = "✅" if is_sel else "⬜️"
        ch_name = ch.get('name', 'Kanal')
        markup.add(
            InlineKeyboardButton(
                text=f"{icon} {ch_name[:26]}",
                callback_data=f"pub_tog_{ch['channel_id']}"
            )
        )

    sel_count = len(selected_ids)
    markup.add(
        InlineKeyboardButton(
            text=f"🚀 Tanlanganlarda boshlash ({sel_count} ta)",
            callback_data="pub_confirm_multi",
            style="success"
        )
    )
    markup.add(
        InlineKeyboardButton(text="🔙 Oddiy tanlovga qaytish", callback_data="pub_back_simple", style="danger")
    )
    return markup


@dp.callback_query_handler(
    text=bt_admin_start_give.callback_data,
    state=CreatedGivesStates.manage_selected_give
)
async def start_give_prompt(jam: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    give_callback_value = state_data.get('give_callback_value')

    channel_model = TelegramChannel()

    # Ushbu adminning botga ulangan barcha kanallarini tekshiramiz
    owner_channels = await channel_model.get_owner_distinct_channels(jam.from_user.id)
    if not owner_channels:
        await jam.answer(
            '⚠️ Sizda hali birorta ham ulangan homiy kanal mavjud emas!\n\n'
            'Iltimos, avval «📢 Kanallar» bo‘limi orqali kamida 1 ta kanal qo‘shing, so‘ngra ishga tushiring.',
            show_alert=True
        )
        return

    # Ushbu konkurs uchun adminning barcha kanallarini ulab qo'yamiz (agar ulanmagan bo'lsa)
    for ch in owner_channels:
        await channel_model.add_channel(
            owner_id=jam.from_user.id,
            channel_id=ch['channel_id'],
            give_callback_value=give_callback_value,
            name=ch['name'],
            group_id=ch.get('group_id', 0)
        )

    channel_data = await channel_model.get_channel_data(
        owner_id=jam.from_user.id,
        give_callback_value=give_callback_value
    )

    await CreatedGivesStates.select_publish_channels.set()
    await state.update_data(
        give_callback_value=give_callback_value,
        selected_publish_channels=[ch['channel_id'] for ch in channel_data]
    )

    if len(channel_data) == 1:
        text = (
            "📢 <b>KONKURSNI QAYSI KANALDA E’LON QILMOQCHISIZ?</b>\n\n"
            f"Sizda 1 ta ulangan kanal mavjud:\n"
            f"👉 <b>«{channel_data[0]['name']}»</b>\n\n"
            "Post aynan shu kanalda e’lon qilinadi. Tasdiqlash uchun quyidagi tugmani bosing:"
        )
    else:
        text = (
            "📢 <b>KONKURSNI QAYSI KANALDA E’LON QILMOQCHISIZ?</b>\n\n"
            f"Sizda <b>{len(channel_data)} ta</b> ulangan kanal mavjud.\n"
            "Post qaysi kanalda e’lon qilinishini tanlang:"
        )

    markup = build_simple_publish_keyboard(channel_data)
    await jam.message.edit_text(text, reply_markup=markup)


@dp.callback_query_handler(
    text='pub_all',
    state=CreatedGivesStates.select_publish_channels
)
async def publish_to_all_channels(jam: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    give_callback_value = state_data['give_callback_value']
    channel_data = await TelegramChannel().get_channel_data(
        owner_id=jam.from_user.id,
        give_callback_value=give_callback_value
    )
    await execute_publish_and_start(
        jam=jam,
        state=state,
        give_callback_value=give_callback_value,
        target_channels=channel_data
    )


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith('pub_single_'),
    state=CreatedGivesStates.select_publish_channels
)
async def publish_to_single_channel(jam: types.CallbackQuery, state: FSMContext):
    try:
        single_channel_id = int(jam.data.replace('pub_single_', ''))
    except ValueError:
        await jam.answer()
        return

    state_data = await state.get_data()
    give_callback_value = state_data['give_callback_value']
    channel_data = await TelegramChannel().get_channel_data(
        owner_id=jam.from_user.id,
        give_callback_value=give_callback_value
    )

    target_channels = [ch for ch in channel_data if ch['channel_id'] == single_channel_id]
    if not target_channels:
        await jam.answer('⚠️ Tanlangan kanal topilmadi!', show_alert=True)
        return

    await execute_publish_and_start(
        jam=jam,
        state=state,
        give_callback_value=give_callback_value,
        target_channels=target_channels
    )


@dp.callback_query_handler(
    text='pub_multi_mode',
    state=CreatedGivesStates.select_publish_channels
)
async def open_multi_mode(jam: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    give_callback_value = state_data['give_callback_value']
    channel_data = await TelegramChannel().get_channel_data(
        owner_id=jam.from_user.id,
        give_callback_value=give_callback_value
    )
    all_ids = [ch['channel_id'] for ch in channel_data]
    await state.update_data(selected_publish_channels=all_ids)

    text = (
        "🎯 <b>BIR NECHTA KANALNI TANLASH</b>\n\n"
        "Post chiqishi kerak bo‘lgan kanallarni belgilang va pastdagi «Boshlash» tugmasini bosing:"
    )
    markup = build_multi_publish_keyboard(channel_data, set(all_ids))
    await jam.answer()
    try:
        await jam.message.edit_text(text, reply_markup=markup)
    except Exception:
        pass


@dp.callback_query_handler(
    text='pub_back_simple',
    state=CreatedGivesStates.select_publish_channels
)
async def back_to_simple_mode(jam: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    give_callback_value = state_data['give_callback_value']
    channel_data = await TelegramChannel().get_channel_data(
        owner_id=jam.from_user.id,
        give_callback_value=give_callback_value
    )
    text = (
        "📢 <b>KONKURSNI QAYSI KANALDA E’LON QILMOQCHISIZ?</b>\n\n"
        f"Ushbu konkursga <b>{len(channel_data)} ta</b> homiy kanal biriktirilgan.\n"
        "Post qaysi kanalda e’lon qilinishini 1 marta bosish orqali tanlang:"
    )
    markup = build_simple_publish_keyboard(channel_data)
    await jam.answer()
    try:
        await jam.message.edit_text(text, reply_markup=markup)
    except Exception:
        pass


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith('pub_tog_'),
    state=CreatedGivesStates.select_publish_channels
)
async def toggle_channel_selection(jam: types.CallbackQuery, state: FSMContext):
    ch_id_str = jam.data.replace('pub_tog_', '')
    try:
        toggled_id = int(ch_id_str)
    except ValueError:
        await jam.answer()
        return

    state_data = await state.get_data()
    selected_ids = list(state_data.get('selected_publish_channels') or [])

    if toggled_id in selected_ids:
        selected_ids.remove(toggled_id)
    else:
        selected_ids.append(toggled_id)

    await state.update_data(selected_publish_channels=selected_ids)

    give_callback_value = state_data['give_callback_value']
    channel_data = await TelegramChannel().get_channel_data(
        owner_id=jam.from_user.id,
        give_callback_value=give_callback_value
    )

    markup = build_multi_publish_keyboard(channel_data, set(selected_ids))
    await jam.answer()
    try:
        await jam.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass


@dp.callback_query_handler(
    text='pub_confirm_multi',
    state=CreatedGivesStates.select_publish_channels
)
async def confirm_multi_selection(jam: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    give_callback_value = state_data['give_callback_value']
    selected_ids = state_data.get('selected_publish_channels') or []

    channel_data = await TelegramChannel().get_channel_data(
        owner_id=jam.from_user.id,
        give_callback_value=give_callback_value
    )

    if not selected_ids:
        await jam.answer('⚠️ Iltimos, kamida 1 ta kanalni tanlang!', show_alert=True)
        return

    target_channels = [ch for ch in channel_data if ch['channel_id'] in selected_ids]
    await execute_publish_and_start(
        jam=jam,
        state=state,
        give_callback_value=give_callback_value,
        target_channels=target_channels
    )


async def execute_publish_and_start(
    jam: types.CallbackQuery,
    state: FSMContext,
    give_callback_value: str,
    target_channels: list
):
    """Tanlangan kanallarda konkursni e'lon qilish va ishga tushirish"""
    give_model = GiveAway()
    channel_model = TelegramChannel()

    give_data = await give_model.get_give_data(
        user_id=jam.from_user.id,
        callback_value=give_callback_value
    )
    if not give_data:
        await jam.answer('⚠️ Konkurs ma’lumotlari topilmadi!')
        return

    give = give_data[0]

    # Barcha homiy kanallar (shartlar uchun)
    all_channel_data = await channel_model.get_channel_data(
        owner_id=jam.from_user.id,
        give_callback_value=give_callback_value
    )

    # Izohli konkurs bo'lsa, tanlangan kanallarga guruh ulanganini tekshirish
    if give["type"] == 'comments':
        for ch in target_channels:
            if not bool(ch.get('group_id')):
                await jam.answer(
                    f"⚠️ «{ch['name']}» kanaliga guruh ulanmagan! Izohli konkurs uchun e’lon qilinadigan har bir kanalda muhokama guruhi bo‘lishi shart.",
                    show_alert=True
                )
                return

    date_str = give['over_date'].strftime('%d.%m.%Y %H:%M') if hasattr(give['over_date'], 'strftime') else str(give['over_date'])

    # Shart kanallar matni va tugmalari
    conditions_lines = []
    channel_buttons = []
    seen_ids = set()
    total_ch = len(all_channel_data)

    for idx, ch in enumerate(all_channel_data, 1):
        if ch['channel_id'] in seen_ids:
            continue
        seen_ids.add(ch['channel_id'])

        ch_name = ch['name']
        if total_ch == 1:
            conditions_lines.append(f"▫️ «{ch_name}» kanaliga obuna bo‘ling")
            btn_title = f"📢 Obuna bo‘lish: {ch_name[:18]} »"
        else:
            conditions_lines.append(f"▫️ {idx}. «{ch_name}» kanaliga obuna bo‘ling")
            btn_title = f"📢 {idx}. {ch_name[:18]} »"

        ch_link = await get_channel_invite_or_username(ch['channel_id'])
        if ch_link:
            channel_buttons.append(InlineKeyboardButton(text=btn_title, url=ch_link))

    conditions_block = ""
    if conditions_lines:
        conditions_block = (
            "📌 <b>Ishtirok etish shartlari:</b>\n"
            + "\n".join(conditions_lines)
            + "\n\n"
        )

    call_to_action = (
        "👇 <b>Qatnashish uchun quyidagi tugmani bosing:</b>"
        if give["type"] == 'button'
        else "💬 <b>Qatnashish uchun ushbu post ostiga izoh yozing!</b>"
    )

    message_text = (
        f"🎁 <b>{give['name'].upper()}</b>\n\n"
        f"{give['text']}\n\n"
        f"{conditions_block}"
        f"🏆 <b>G‘oliblar soni:</b> {give['winners_count']} nafar\n"
        f"⏳ <b>Yakunlanish vaqti:</b> {date_str}\n"
        f"🛡 <b>Himoya:</b> Kaptcha va shaffof filtr\n\n"
        f"{call_to_action}"
    )

    bot_data = await bot.get_me()
    markup = InlineKeyboardMarkup()
    for btn in channel_buttons:
        markup.add(btn)

    markup.add(
        InlineKeyboardButton(
            text='🎁 Qatnashish (0) »',
            url=f'https://t.me/{bot_data.username}?start={give_callback_value}'
        )
    )

    published_names = []
    failed_names = []
    primary_post_link = ''

    for channel in target_channels:
        try:
            message = None
            if give["photo_id"] is None and give["video_id"] is None:
                message = await bot.send_message(
                    chat_id=channel['channel_id'],
                    text=message_text,
                    reply_markup=markup if give["type"] == 'button' else None
                )
            elif give["photo_id"]:
                message = await bot.send_photo(
                    chat_id=channel['channel_id'],
                    photo=give["photo_id"],
                    caption=message_text,
                    reply_markup=markup if give["type"] == 'button' else None
                )
            elif give["video_id"]:
                message = await bot.send_video(
                    chat_id=channel['channel_id'],
                    video=give["video_id"],
                    caption=message_text,
                    reply_markup=markup if give["type"] == 'button' else None
                )

            if message:
                # Har bir kanalning o'z post_id ini bazada saqlaymiz
                cb_val = channel.get('channel_callback_value')
                if cb_val:
                    await TelegramChannel.filter(
                        channel_callback_value=cb_val
                    ).update(post_id=message.message_id)
                else:
                    await TelegramChannel.filter(
                        channel_id=channel['channel_id'],
                        give_callback_value=give_callback_value
                    ).update(post_id=message.message_id)

                published_names.append(channel['name'])

                if not primary_post_link:
                    if message.chat.username:
                        chat_url = f"https://t.me/{message.chat.username}"
                    else:
                        chat_url = await message.chat.get_url() if hasattr(message.chat, 'get_url') else ""
                    primary_post_link = f"{chat_url}/{message.message_id}" if chat_url else str(message.message_id)

        except Exception as e:
            failed_names.append(f"«{channel['name']}» ({e})")

    if not published_names:
        error_msg = "\n".join(failed_names)
        await jam.answer(
            f'⚠️ Kanallarga post chiqarishda xatolik yuz berdi:\n{error_msg}\n\nBot kanalda admin ekanligini va xabar yuborish huquqi borligini tekshiring!',
            show_alert=True
        )
        return

    # Statistika yozish
    await GiveAwayStatistic().add_statistic(
        giveaway_callback_value=give_callback_value,
        members=[],
        winners=[],
        post_link=primary_post_link
    )

    # Konkurs holatini faol qilish
    await give_model.update_give_status(
        callback_value=give_callback_value,
        status=True
    )

    pub_list_text = "\n".join([f"  ✅ «{name}»" for name in published_names])
    fail_text = ""
    if failed_names:
        fail_text = "\n\n⚠️ <b>Yuborib bo‘linmagan kanallar:</b>\n" + "\n".join([f"  ❌ {name}" for name in failed_names])

    await jam.message.edit_text(
        f'🚀 <b>KONKURS MUVAFFAQIYATLI ISHGA TUSHIRILDI!</b> ✅\n\n'
        f'📢 <b>Post e’lon qilingan kanal(lar):</b>\n'
        f'{pub_list_text}'
        f'{fail_text}\n\n'
        'Post belgilangan kanallarga joylashtirildi va ishtirokchilar qabul qilinmoqda.\n\n'
        'Jarayonni <b>🚀 Faol konkurslar</b> bo‘limida kuzatishingiz mumkin.',
        reply_markup=kb_admin_menu
    )
    await state.finish()
