from app import dp, bot
from config import OWNERS


@dp.errors_handler(
    exception=Exception
)
async def handle_bot_exceptions(
        update,
        error
):
    user_id = "Noma'lum"
    username = "Noma'lum"
    message_text = "Mavjud emas"

    try:
        if isinstance(update, dict):
            from_user = (update.get('message', {}).get('from') or 
                         update.get('callback_query', {}).get('from') or {})
            if from_user:
                user_id = from_user.get('id', user_id)
                username = from_user.get('username', username)
            msg = update.get('message') or (update.get('callback_query', {}).get('message') if update.get('callback_query') else None)
            if msg:
                message_text = msg.get('text', message_text)
        elif hasattr(update, 'message') and update.message:
            user_id = update.message.from_user.id
            username = update.message.from_user.username
            message_text = update.message.text
        elif hasattr(update, 'callback_query') and update.callback_query:
            user_id = update.callback_query.from_user.id
            username = update.callback_query.from_user.username
            message_text = update.callback_query.data
    except Exception:
        pass

    for owner_id in OWNERS:
        try:
            await bot.send_message(
                chat_id=owner_id,
                text=(
                    f"🚨 <b>Kutilmagan xatolik yuz berdi!</b>\n\n"
                    f"👤 <b>Foydalanuvchi ID:</b> <code>{user_id}</code>\n"
                    f"🔹 <b>Username:</b> @{username}\n\n"
                    f"💬 <b>Xabar / Callback:</b>\n<code>{message_text}</code>\n\n"
                    f"⚠️ <b>Xatolik matni:</b>\n<code>{error}</code>"
                )
            )
        except Exception:
            pass

    return True
