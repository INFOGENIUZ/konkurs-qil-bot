from app import bot
from database import GiveAwayStatistic


async def send_giveaway_end_notification(
    give_callback_value: str
):
    statistic_data = await GiveAwayStatistic().get_data(
        giveaway_callback_value=give_callback_value
    )

    members = statistic_data[0]['members']
    for member in members:
        await bot.send_message(
            chat_id=member['user_id'],
            text='⏳ <b>Diqqat! Konkurs tez orada yakunlanadi — shoshiling!</b> 💎'
        )
