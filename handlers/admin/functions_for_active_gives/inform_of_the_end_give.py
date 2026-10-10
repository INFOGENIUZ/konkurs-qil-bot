from app import bot
from database import GiveAway, TelegramChannel, TemporaryUsers


async def delete_and_inform_of_the_end_give(
    give_callback_value: str,
    winners: list,
    summary_count_users: int,
):
    give_data = await GiveAway().filter(callback_value=give_callback_value).all().values(
        'owner_id',
        'name'
    )

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    for give in give_data:

        if summary_count_users >= len(winners) and len(winners) > 0:

            text = (
                f"🎁 <b>Konkurs muvaffaqiyatli yakunlandi!</b>\n\n"
                f"📌 <b>Nomi:</b> {give['name']}\n"
                f"👥 <b>Jami ishtirokchilar soni:</b> {summary_count_users} ta\n\n"
                f"🏆 <b>G‘oliblar ro‘yxati:</b>\n\n"
            )
            for i in range(len(winners)):
                user_info = winners[i]
                place = user_info.get('place', i + 1)
                medal = medals.get(place, "🎖")
                text += f"{medal} <b>{place}-o‘rin:</b> @{user_info['username']}"
                if i < len(winners) - 1:
                    text += "\n"

            await bot.send_message(
                chat_id=give['owner_id'],
                text=text
            )

        else:
            await bot.send_message(
                chat_id=give['owner_id'],
                text=(
                    f"🎁 <b>Konkurs yakunlandi!</b>\n\n"
                    f"📌 <b>Nomi:</b> {give['name']}\n"
                    f"⚠️ <b>G‘oliblarni aniqlab bo‘lmadi, ishtirokchilar soni yetarli emas.</b>"
                )
            )


    await GiveAway().delete_give(callback_value=give_callback_value)
    await TemporaryUsers().filter(giveaway_callback_value=give_callback_value).delete()
