from urllib.parse import quote
from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp, bot
from database import GiveAway, GiveAwayStatistic
from utils import Captcha


captcha = Captcha()


def build_participant_card(
    give_name: str,
    ticket_number: str,
    user_display: str,
    members_count: int,
    winners_count: int,
    date_str: str,
    give_callback_value: str,
    bot_username: str,
    post_link: str = None,
    is_already: bool = False
) -> tuple[str, types.InlineKeyboardMarkup]:
    if is_already:
        text = (
            "ℹ️ <b>ALLAQACHON RO‘YXATDASIZ</b> ✅\n\n"
            f"Siz allaqachon «<b>{give_name}</b>» konkursining rasmiy ishtirokchisiga aylangansiz!\n\n"
            f"🎫 <b>Sizning chiptangiz:</b> <code>{ticket_number}</code>\n"
            f"👤 <b>Ishtirokchi:</b> {user_display}\n"
            f"👥 <b>Jami ishtirokchilar:</b> <code>{members_count} nafar</code>\n"
            f"🏆 <b>G‘oliblar soni:</b> <code>{winners_count} nafar</code>\n"
            f"⏳ <b>Yakunlanish vaqti:</b> <code>{date_str}</code>\n\n"
            "⏳ <i>Natijalarni kuting! G‘oliblar belgilangan vaqtda bot va kanalda e’lon qilinadi.</i>"
        )
    else:
        text = (
            "🎉 <b>TABRIKLAYMIZ! RO‘YXATGA OLINDINGIZ</b> ✅\n\n"
            f"Siz «<b>{give_name}</b>» konkursining rasmiy ishtirokchisiga aylandingiz!\n\n"
            f"🎫 <b>Sizning chiptangiz:</b> <code>{ticket_number}</code>\n"
            f"👤 <b>Ishtirokchi:</b> {user_display}\n"
            f"👥 <b>Jami ishtirokchilar:</b> <code>{members_count} nafar</code>\n"
            f"🏆 <b>G‘oliblar soni:</b> <code>{winners_count} nafar</code>\n"
            f"⏳ <b>Yakunlanish vaqti:</b> <code>{date_str}</code>\n\n"
            "🍀 <i>Sizga omad tilaymiz! G‘oliblar tizim tomonidan avtomatik va shaffof tarzda aniqlanadi.</i>"
        )

    markup = types.InlineKeyboardMarkup(row_width=1)
    share_text = f"🎁 {give_name} konkursida ishtirok eting va ajoyib sovg‘alarni yutib oling!"
    share_url = f"https://t.me/{bot_username}?start={give_callback_value}"
    share_full = f"https://t.me/share/url?url={quote(share_url)}&text={quote(share_text)}"

    markup.add(
        types.InlineKeyboardButton(
            text="📢 Do‘stlarga ulashish (Share) »",
            url=share_full
        )
    )

    if post_link and (post_link.startswith("http://") or post_link.startswith("https://") or post_link.startswith("tg://")):
        markup.add(
            types.InlineKeyboardButton(
                text="🔗 Konkurs postini ko‘rish »",
                url=post_link
            )
        )

    return text, markup


async def send_participant_card(
    user: types.User,
    give_callback_value: str,
    is_already: bool = False
):
    try:
        give_data = await GiveAway().filter(callback_value=give_callback_value).all().values(
            'name',
            'over_date',
            'winners_count'
        )
        if not give_data:
            return

        give = give_data[0]
        give_name = give.get('name', 'Konkurs')
        over_date = give.get('over_date')
        date_str = over_date.strftime('%d.%m.%Y %H:%M') if hasattr(over_date, 'strftime') else str(over_date)
        winners_count = give.get('winners_count', 1)

        stat_data = await GiveAwayStatistic().filter(giveaway_callback_value=give_callback_value).all().values(
            'post_link'
        )
        post_link = stat_data[0]['post_link'] if stat_data and stat_data[0].get('post_link') else ""

        ticket_number = await GiveAwayStatistic().get_member_ticket(
            giveaway_callback_value=give_callback_value,
            member_id=user.id,
            member_username=user.username
        )
        members_count = await GiveAwayStatistic().get_members_count(giveaway_callback_value=give_callback_value)

        bot_info = await bot.get_me()
        user_display = f"@{user.username}" if user.username else user.full_name

        text, markup = build_participant_card(
            give_name=give_name,
            ticket_number=ticket_number,
            user_display=user_display,
            members_count=members_count,
            winners_count=winners_count,
            date_str=date_str,
            give_callback_value=give_callback_value,
            bot_username=bot_info.username,
            post_link=post_link,
            is_already=is_already
        )

        await bot.send_message(
            chat_id=user.id,
            text=text,
            reply_markup=markup
        )
    except Exception as e:
        import logging
        logging.error(f"Error sending participant card: {e}")


async def manage_new_members_from_button_gives(
    jam: types.Message | types.CallbackQuery,
    give_callback_value: str,
    state: FSMContext,
    user: types.User = None
):
    if user is None:
        user = jam.from_user

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

    give_data = await GiveAway().filter(callback_value=give_callback_value).all().values(
        'over_date',
        'captcha'
    )

    if not give_data:
        return

    give = give_data[0]

    if give['captcha']:
        await state.update_data(give_callback_value=give_callback_value)
        captcha.register_handlers(dp)
        await bot.send_message(
            user.id,
            captcha.get_caption(),
            reply_markup=captcha.get_captcha_keyboard()
        )
    else:
        updated = await GiveAwayStatistic().update_statistic_members(
            giveaway_callback_value=give_callback_value,
            new_member_username=user.username,
            new_member_id=user.id
        )

        if updated:
            from .update_channel_post import update_giveaway_post_buttons
            await update_giveaway_post_buttons(give_callback_value)

        await send_participant_card(
            user=user,
            give_callback_value=give_callback_value,
            is_already=False
        )
