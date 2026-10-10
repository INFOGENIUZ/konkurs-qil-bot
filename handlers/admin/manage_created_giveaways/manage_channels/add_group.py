from aiogram import types
from aiogram.dispatcher import FSMContext

from app import bot, dp
from database import TelegramChannel
from keyboards import *
from states import CreatedGivesStates



@dp.callback_query_handler(
    text=bt_admin_add_group_for_channel.callback_data,
    state=CreatedGivesStates.show_connected_channel
)
async def add_new_group_for_channel(
        jam: types.CallbackQuery,
        state: FSMContext
):
    state_data = await state.get_data()

    bot_data = await bot.get_me()
    await jam.message.edit_text(
        f'1️⃣ Botni (@{bot_data.username}) guruhga administrator qilib qo‘shing:\n'
        f'<code>- Xabarlarni yuborish\n- Boshqa xabarlarni tahrirlash</code>\n\n'
        f'2️⃣ Guruhdan biror xabarni bu yerga forward (repost) qilib yuboring:',
        reply_markup=kb_admin_cancel_action
    )
    await CreatedGivesStates.add_group.set()





@dp.message_handler(
    state=CreatedGivesStates.add_group,
)
async def get_group_data(
    jam: types.Message,
    state: FSMContext
):
    try:

        group_data = jam.forward_from_chat

        if group_data and group_data.type in ['group', 'supergroup']:

            member_info = await bot.get_chat_member(
                chat_id=group_data.id,
                user_id=bot.id
            )

            if member_info.status == 'administrator':
                state_data = await state.get_data()
                channel_callback_value = state_data['channel_callback_value']

                target_ch = await TelegramChannel.filter(channel_callback_value=channel_callback_value).first()
                if target_ch:
                    await TelegramChannel.filter(
                        owner_id=target_ch.owner_id,
                        channel_id=target_ch.channel_id
                    ).update(group_id=group_data.id)
                else:
                    await TelegramChannel.filter(channel_callback_value=channel_callback_value).update(
                        group_id=group_data.id
                    )

                await jam.answer(
                    '✅ <b>Guruh muvaffaqiyatli ulandi!</b>',
                    reply_markup=kb_admin_manage_channels
                )
                await CreatedGivesStates.manage_channels.set()


        else:
            await jam.answer(
                '🚫 <b>Bu guruh emas!</b> Iltimos, faqat guruhdan biror xabarni forward qiling:',
                reply_markup=kb_admin_cancel_action
            )


    except Exception:
        await jam.answer(
            '🚫 <b>Xatolik!</b> Bot guruhda administrator ekanligiga ishonch hosil qiling va xabarni qayta forward qiling:',
            reply_markup=kb_admin_cancel_action
        )
