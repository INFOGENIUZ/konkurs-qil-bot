from aiogram import types
from aiogram.dispatcher import FSMContext

from app import bot, dp
from database import TelegramChannel
from states import CreatedGivesStates
from keyboards import *


@dp.callback_query_handler(
    text=[
        bt_admin_active_channels.callback_data,
        bt_admin_add_channel.callback_data
    ],
    state=CreatedGivesStates.manage_channels
)
async def manage_channels(
    jam: types.CallbackQuery,
    state: FSMContext
):
    callback = jam.data

    if callback == bt_admin_active_channels.callback_data:

        state_data = await state.get_data()
        give_callback_value = state_data.get('give_callback_value', False)

        markup = await TelegramChannel().get_keyboard(
            owner_id=jam.from_user.id,
            give_callback_value=give_callback_value
        )

        if not markup and give_callback_value:
            owner_channels = await TelegramChannel().get_owner_distinct_channels(jam.from_user.id)
            if owner_channels:
                for ch in owner_channels:
                    await TelegramChannel().add_channel(
                        owner_id=jam.from_user.id,
                        channel_id=ch['channel_id'],
                        give_callback_value=give_callback_value,
                        name=ch['name'],
                        group_id=ch.get('group_id', 0)
                    )
                markup = await TelegramChannel().get_keyboard(
                    owner_id=jam.from_user.id,
                    give_callback_value=give_callback_value
                )

        if markup:
            markup.add(bt_admin_cancel_action)

            await jam.message.edit_text(
                '📢 <b>ULANGAN KANALLAR</b>\n\n'
                'Boshqarish yoki guruh ulash uchun kerakli kanalni tanlang:',
                reply_markup=markup
            )
            await CreatedGivesStates.select_connected_channel.set()

        else:
            await jam.answer('⚠️ Sizda hali ulangan homiy kanallar mavjud emas!')

    else:
        bot_data = await bot.get_me()

        await jam.message.edit_text(
            f'➕ <b>YANGI KANAL QO‘SHISH</b>\n\n'
            f'Kanalni botga ulash uchun quyidagi 2 ta qadamni bajaring:\n\n'
            f'1️⃣ <b>Botni kanalga admin qilish:</b>\n'
            f'Botimizni (@{bot_data.username}) kanalingizga administrator qilib tayinlang va quyidagi huquqni bering:\n'
            f'  • <i>Xabarlarni yuborish (Post messages)</i>\n\n'
            f'2️⃣ <b>Kanal havolasini yuborish:</b>\n'
            f'Kanalingiz havolasini yoki @username\'ini botga yuboring 🔗\n'
            f'<i>(Masalan: https://t.me/kanal_nomi yoki @kanal_nomi)</i>\n\n'
            f'❌ Bekor qilish uchun quyidagi tugmani bosing.',
            reply_markup=kb_admin_cancel_action
        )
        await CreatedGivesStates.add_channel.set()
