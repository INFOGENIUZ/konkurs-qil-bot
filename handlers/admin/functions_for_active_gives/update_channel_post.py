from app import bot
from database import GiveAway, TelegramChannel, GiveAwayStatistic
from keyboards import InlineKeyboardMarkup, InlineKeyboardButton
from .check_channels_subscriptions import get_channel_invite_or_username


async def update_giveaway_post_buttons(give_callback_value: str):
    """Konkurs postidagi Qatnashish tugmasini yangi ishtirokchilar soni bilan yangilash"""
    try:
        give = await GiveAway.filter(callback_value=give_callback_value).first()
        if not give or give.type != 'button':
            return

        stat = await GiveAwayStatistic.filter(giveaway_callback_value=give_callback_value).first()
        members_count = len(stat.members) if stat and stat.members else 0

        # Homiy kanallar shartlari
        all_channel_data = await TelegramChannel().get_channel_data(
            owner_id=give.owner_id,
            give_callback_value=give_callback_value
        )

        bot_data = await bot.get_me()
        markup = InlineKeyboardMarkup()

        seen_ids = set()
        idx = 1
        total_ch = len(all_channel_data)
        for ch in all_channel_data:
            if ch['channel_id'] in seen_ids:
                continue
            seen_ids.add(ch['channel_id'])
            ch_link = await get_channel_invite_or_username(ch['channel_id'])
            if ch_link:
                ch_name = ch.get('name', 'Kanal')
                if total_ch == 1:
                    btn_title = f"📢 Obuna bo‘lish: {ch_name[:18]} »"
                else:
                    btn_title = f"📢 {idx}. {ch_name[:18]} »"
                markup.add(InlineKeyboardButton(text=btn_title, url=ch_link))
                idx += 1

        # Yangilangan ishtirokchilar soni bilan Qatnashish tugmasi
        markup.add(
            InlineKeyboardButton(
                text=f'🎁 Qatnashish ({members_count}) »',
                url=f'https://t.me/{bot_data.username}?start={give_callback_value}'
            )
        )

        # Post e'lon qilingan kanallarda tugmani tahrirlaymiz
        published_channels = await TelegramChannel.filter(
            give_callback_value=give_callback_value,
            post_id__isnull=False
        ).all()

        for ch in published_channels:
            if ch.post_id:
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=ch.channel_id,
                        message_id=ch.post_id,
                        reply_markup=markup
                    )
                except Exception as e:
                    import logging
                    logging.info(f"Notice editing post markup: {e}")
    except Exception as e:
        import logging
        logging.error(f"Error in update_giveaway_post_buttons: {e}")
