import io
import json
from datetime import datetime

from aiogram import types
from aiogram.types import InputFile

from app import bot, dp
from config import OWNERS, timezone_info
from database import GiveAway, TelegramChannel, BotUser, GiveAwayStatistic, MandatoryChannel


@dp.callback_query_handler(text='owner_backup', state='*')
async def owner_generate_backup(jam: types.CallbackQuery):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    await jam.answer("⏳ Zaxira nusxa tayyorlanmoqda...", show_alert=False)

    users = await BotUser.all().values('user_id', 'username', 'first_name', 'created_at', 'is_blocked')
    for u in users:
        if u.get('created_at'):
            u['created_at'] = str(u['created_at'])

    gives = await GiveAway.all().values(
        'name', 'callback_value', 'owner_id', 'run_status', 'type', 'over_date', 'winners_count', 'captcha'
    )
    for g in gives:
        if g.get('over_date'):
            g['over_date'] = str(g['over_date'])

    channels = await TelegramChannel.all().values(
        'channel_id', 'name', 'owner_id', 'give_callback_value', 'post_id', 'group_id'
    )

    mandatories = await MandatoryChannel.all().values(
        'channel_id', 'name', 'invite_link', 'is_active'
    )

    stats = await GiveAwayStatistic.all().values(
        'giveaway_callback_value', 'members', 'winners', 'post_link'
    )

    backup_data = {
        'generated_at': str(datetime.now(timezone_info)),
        'total_users': len(users),
        'total_giveaways': len(gives),
        'total_channels': len(channels),
        'users': users,
        'giveaways': gives,
        'channels': channels,
        'mandatory_channels': mandatories,
        'statistics': stats
    }

    json_str = json.dumps(backup_data, ensure_ascii=False, indent=2)
    file_bytes = io.BytesIO(json_str.encode('utf-8'))
    date_tag = datetime.now(timezone_info).strftime('%Y-%m-%d_%H-%M')
    file_bytes.name = f"bot_backup_{date_tag}.json"

    doc = InputFile(file_bytes, filename=f"bot_backup_{date_tag}.json")
    await bot.send_document(
        chat_id=jam.from_user.id,
        document=doc,
        caption=(
            f"💾 <b>BAZA ZAXIRA NUSXASI (BACKUP)</b> ✅\n\n"
            f"📅 Sana: <code>{date_tag}</code>\n"
            f"👥 Jami foydalanuvchilar: <code>{len(users)} ta</code>\n"
            f"🎁 Jami konkurslar: <code>{len(gives)} ta</code>\n"
            f"📢 Jami kanallar: <code>{len(channels)} ta</code>\n\n"
            "<i>Ushbu faylni xavfsiz saqlang!</i>"
        )
    )
