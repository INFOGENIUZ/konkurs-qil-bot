from aiogram import types

from database import TelegramChannel, GiveAwayStatistic
from .check_channels_subscriptions import check_channels_subscriptions
from config import text_for_participation_in_comments_giveaways


async def handle_new_users_in_groups(message: types.Message):
    try:
        if not message.text:
            return

        msg_clean = message.text.strip().lower()
        keyword_clean = text_for_participation_in_comments_giveaways.strip().lower()

        if msg_clean == keyword_clean or msg_clean in ['qatnashaman', 'участвую']:

            give_data = await TelegramChannel().filter(group_id=message.chat.id).all().values(
                'give_callback_value',
                'post_id',
                'owner_id'
            )


            for give in give_data:

                if await check_channels_subscriptions(
                        give_callback_value=give['give_callback_value'],
                        user_id=message.from_user.id,
                        owner_id=give['owner_id']
                ):

                    if give.get('post_id') and message.reply_to_message and getattr(message.reply_to_message, 'forward_from_message_id', None) == int(give['post_id']):

                        if await GiveAwayStatistic().update_statistic_members(
                            giveaway_callback_value=give['give_callback_value'],
                            new_member_username=message.from_user.username,
                            new_member_id=message.from_user.id,
                        ):
                            from .update_channel_post import update_giveaway_post_buttons
                            await update_giveaway_post_buttons(give['give_callback_value'])

                            await message.reply(
                                '🎉 <b>Ishtirokingiz qabul qilindi! Siz konkursda muvaffaqiyatli ro‘yxatga olindingiz!</b> ✅'
                            )

                else:
                    await message.reply(
                        '⚠️ <b>Diqqat! Siz barcha homiy kanallarga obuna bo‘lmagansiz!</b> 📌',
                    )

    except (AttributeError, TypeError):
        return
