from database import GiveAway, TelegramChannel
from app import bot


async def get_channel_invite_or_username(channel_id: int) -> str:
    """Kanalning havola manzilini (username yoki invite_link) avtomatik olish"""
    try:
        chat = await bot.get_chat(channel_id)
        if chat.username:
            return f"https://t.me/{chat.username}"
        elif chat.invite_link:
            return chat.invite_link
        else:
            return await bot.export_chat_invite_link(channel_id)
    except Exception:
        return ""


async def get_channels_subscription_details(
        give_callback_value: str,
        user_id: int,
        owner_id: int = False
) -> list[dict]:
    """Har bir kanal bo‘yicha a’zolik holati va havolalarini batafsil qaytarish"""
    if not owner_id:
        try:
            owner_id = await GiveAway().get_owner_by_callback_value(
                give_callback_value=give_callback_value
            )
        except (IndexError, KeyError):
            return []

    channels_data = await TelegramChannel().get_channel_data(
        owner_id=owner_id,
        give_callback_value=give_callback_value
    )

    results = []
    for channel in channels_data:
        channel_id = channel['channel_id']
        channel_name = channel.get('name', 'Kanal')
        is_subscribed = False

        try:
            user_channel_info = await bot.get_chat_member(
                chat_id=channel_id,
                user_id=user_id
            )
            if user_channel_info.status in ['member', 'administrator', 'creator']:
                is_subscribed = True
        except Exception:
            is_subscribed = False

        link = await get_channel_invite_or_username(channel_id)

        results.append({
            'channel_id': channel_id,
            'name': channel_name,
            'is_subscribed': is_subscribed,
            'link': link
        })

    return results


async def check_channels_subscriptions(
        give_callback_value: str,
        user_id: int,
        owner_id: int = False
) -> bool:
    """Umumiy tekshiruv: barcha kanallarga obuna bo‘linganmi?"""
    details = await get_channels_subscription_details(
        give_callback_value=give_callback_value,
        user_id=user_id,
        owner_id=owner_id
    )
    if not details:
        return True
    return all(ch['is_subscribed'] for ch in details)
