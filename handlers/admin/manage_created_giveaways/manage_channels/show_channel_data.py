from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from database import TelegramChannel
from states import CreatedGivesStates
from keyboards import *


@dp.callback_query_handler(
    lambda c: c.data != bt_admin_cancel_action.callback_data,
    state=CreatedGivesStates.select_connected_channel,
)
async def show_selected_channel(
    jam: types.CallbackQuery,
    state: FSMContext
):
    channel_callback_value = jam.data
    await state.update_data(channel_callback_value=channel_callback_value)

    channel_data = await TelegramChannel().get_channel_data(
        channel_callback_value=channel_callback_value
    )

    for channel in channel_data:
        group_str = f"<code>{channel['group_id']}</code>" if channel.get('group_id') else "<i>❌ Ulanmagan</i>"
        message_text = (
            f"📢 <b>KANAL MA’LUMOTLARI</b>\n\n"
            f"🏷 <b>Kanal nomi:</b> <code>{channel['name']}</code>\n"
            f"🆔 <b>Kanal ID:</b> <code>{channel['channel_id']}</code>\n"
            f"💬 <b>Bog‘langan guruh:</b> {group_str}\n"
            f"🤖 <b>Bot maqomi:</b> 🟢 <i>Administrator</i>\n\n"
            f"💡 <i>Quyidagi tugmalar orqali guruh bog‘lash yoki kanalni o‘chirish mumkin:</i>"
        )
        await jam.message.edit_text(
            message_text,
            reply_markup=kb_admin_manage_selected_channel
        )

    await CreatedGivesStates.show_connected_channel.set()
