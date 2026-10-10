from aiogram import types
from app import dp
from database import GiveAway
from keyboards import *
from states import ActiveGivesStates


@dp.callback_query_handler(
    text=bt_admin_started_gives.callback_data,
    state='*'
)
async def show_active_gives(jam: types.CallbackQuery):
    markup = await GiveAway().get_keyboard_of_active_gives(
        user_id=jam.from_user.id
    )

    if markup:
        markup.add(bt_admin_cancel_action)

        await jam.message.edit_text(
            '🚀 <b>Ko‘rish uchun faol konkursni tanlang:</b>',
            reply_markup=markup
        )
        await ActiveGivesStates.select_give.set()

    else:
        await jam.answer('⚠️ Sizda faol konkurslar mavjud emas!')
