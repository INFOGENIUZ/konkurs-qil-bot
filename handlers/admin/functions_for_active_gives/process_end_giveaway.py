from database import GiveAway, TelegramChannel, GiveAwayStatistic
from .winners_animation import run_winners_animation



async def process_end_of_giveaway(
        give_callback_value: str,
        owner_id: int
):
    winners_data = await GiveAway().filter(callback_value=give_callback_value).all().values('winners_count')
    channels_data = await TelegramChannel().get_channel_data(
        owner_id=owner_id,
        give_callback_value=give_callback_value
    )
    statistic_data = await GiveAwayStatistic().filter(giveaway_callback_value=give_callback_value).all().values(
        'members',
        'winners'
    )


    if not winners_data:
        return
    winners_count = winners_data[0]['winners_count']

    # Faqat post chiqarilgan belgilangan kanallar
    published_channels = [ch for ch in channels_data if ch.get('post_id')]
    if not published_channels:
        published_channels = channels_data

    channel_ids = [ch['channel_id'] for ch in published_channels]
    members = statistic_data[0]['members'] if statistic_data and statistic_data[0].get('members') else []
    existing_winners = statistic_data[0]['winners'] if statistic_data and statistic_data[0].get('winners') else []

    await run_winners_animation(
        give_callback_value=give_callback_value,
        channel_ids=channel_ids,
        members_from_giveaway=members,
        winners_count=winners_count,
        winners_users=existing_winners
    )
