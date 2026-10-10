import asyncio
import random

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified

from app import bot
from database import TemporaryUsers, GiveAwayStatistic

from .inform_of_the_end_give import delete_and_inform_of_the_end_give



async def create_markup_for_watch_results(
        give_callback_value: str
) -> InlineKeyboardMarkup:

    bot_data = await bot.get_me()
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            text='👀 Natijalarni kuzatish »',
            url=f'https://t.me/{bot_data.username}?start={give_callback_value}=watchresult'
        )
    )

    return markup



async def create_markup_for_watch_winners(
        give_callback_value: str
) -> InlineKeyboardMarkup:

    bot_data = await bot.get_me()
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            text='🏆 Natijalarni ko‘rish »',
            url=f'https://t.me/{bot_data.username}?start={give_callback_value}=getresults'
        )
    )

    return markup



async def run_winners_animation(
    give_callback_value: str,
    channel_ids: list | int,
    members_from_giveaway: list,
    winners_count: int,
    winners_users: list = False
):
    if isinstance(channel_ids, int):
        channel_ids = [channel_ids]

    summary_members_count = len(members_from_giveaway)
    if len(members_from_giveaway) >= winners_count:

        markup = await create_markup_for_watch_results(give_callback_value)
        for ch_id in channel_ids:
            try:
                await bot.send_message(
                    chat_id=ch_id,
                    text='💎 <b>G‘oliblarni aniqlash boshlanishiga 10 daqiqa qoldi</b> ⏳',
                    reply_markup=markup
                )
            except Exception:
                pass
        await asyncio.sleep(20)

        if not winners_users:
            winners_users = []
            chosen_winners = random.sample(members_from_giveaway, min(winners_count, len(members_from_giveaway)))
            for place_number, member_info in enumerate(chosen_winners, start=1):
                winners_users.append({
                    'place': place_number,
                    'user_id': member_info['user_id'],
                    'username': member_info['username']
                })
                if member_info in members_from_giveaway:
                    members_from_giveaway.remove(member_info)


        temporary_users_for_watch_results = await TemporaryUsers().get_all_users(
            callback_value=give_callback_value
        )

        if temporary_users_for_watch_results:
            users_to_send_messages = []

            for user in temporary_users_for_watch_results:
                try:
                    message = await bot.send_message(
                        chat_id=user['user_id'],
                        text='🎲 <b>G‘oliblarni tasodifiy tanlash jarayoni boshlanmoqda...</b> ⏳'
                    )

                    users_to_send_messages.append(
                        {
                            'user_id': user['user_id'],
                            'message_id': message.message_id
                        }
                    )
                except Exception:
                    continue


            members_usernames = [m['username'] for m in members_from_giveaway if m.get('username')]

            while len(members_usernames) > 1:
                username = ''
                text = ''

                try:
                    chunks = [
                        members_usernames[i:i + 12]
                        for i in range(0, len(members_usernames), 8)
                    ]

                    for chunk in chunks:
                        if not chunk:
                            continue
                        index = random.randint(0, len(chunk) - 1)
                        username = chunk[index]

                        chunk.pop(index)
                        if username in members_usernames:
                            members_usernames.remove(username)

                        users_formatted = [f'🎁 @{user}  ' for user in chunk]
                        text = ''

                        for i, user in enumerate(users_formatted):
                            if i % 4 == 0 and i > 0:
                                text += '\n'

                            text += user + ' '

                    for user_to_send in users_to_send_messages:
                        try:
                            await bot.edit_message_text(
                                chat_id=user_to_send['user_id'],
                                message_id=user_to_send['message_id'],
                                text=f'❌ <b>Chiqib ketmoqda: @{username}</b>\n\n<b>{text}</b>'
                            )
                        except (MessageNotModified, Exception):
                            continue

                    await asyncio.sleep(0.5)

                except (ValueError, IndexError):
                    break

            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            text = "🏆 <b>Konkurs g‘oliblari:</b>\n\n"
            for i in range(len(winners_users)):
                user_info = winners_users[i]
                place = user_info.get('place', i + 1)
                medal = medals.get(place, "🎖")
                text += f"{medal} <b>{place}-o‘rin:</b> @{user_info['username']}\n"

            for user_to_send in users_to_send_messages:
                try:
                    await bot.edit_message_text(
                        chat_id=user_to_send['user_id'],
                        message_id=user_to_send['message_id'],
                        text=text
                    )
                except Exception:
                    continue


        await GiveAwayStatistic().filter(
            giveaway_callback_value=give_callback_value
        ).update(
            winners=winners_users
        )


        markup = await create_markup_for_watch_winners(give_callback_value)
        for ch_id in channel_ids:
            try:
                await bot.send_message(
                    chat_id=ch_id,
                    text='🎉 <b>Konkurs yakunlandi!</b> ✅',
                    reply_markup=markup
                )
            except Exception:
                pass

    else:
        for ch_id in channel_ids:
            try:
                await bot.send_message(
                    chat_id=ch_id,
                    text='⚠️ <b>Konkurs yakunlandi! Ishtirokchilar soni kamligi sababli g‘oliblarni aniqlab bo‘lmadi.</b>',
                )
            except Exception:
                pass


    await delete_and_inform_of_the_end_give(
        give_callback_value=give_callback_value,
        winners=winners_users,
        summary_count_users=summary_members_count
    )
