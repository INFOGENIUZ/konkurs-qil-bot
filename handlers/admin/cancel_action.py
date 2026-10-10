from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from database import TelegramChannel

from keyboards import bt_admin_cancel_action, kb_admin_menu, kb_main_menu
from states import CreateGiveStates, CreatedGivesStates

from .manage_created_giveaways import show_created_gives, show_selected_give, process_manage_channels
from config import start_text


@dp.callback_query_handler(
    text=bt_admin_cancel_action.callback_data,
    state='*'
)
async def cancel_admin_action(
    jam: types.CallbackQuery,
    state: FSMContext
):
    current_state = await state.get_state()

    if current_state in CreateGiveStates.states_names:
        await jam.message.edit_text(
            start_text,
            reply_markup=kb_admin_menu
        )
        await state.finish()

    elif current_state == CreatedGivesStates.select_publish_channels.state:
        state_data = await state.get_data()
        if state_data.get('give_callback_value'):
            await show_selected_give(
                jam=jam,
                state=state,
                give_callback_value=state_data['give_callback_value']
            )
        else:
            await show_created_gives(jam=jam)

    elif current_state == CreatedGivesStates.manage_selected_give.state:
        await show_created_gives(
            jam=jam
        )

    elif current_state == CreatedGivesStates.select_give.state:
        await jam.message.edit_text(
            start_text,
            reply_markup=kb_admin_menu
        )
        await state.finish()

    elif current_state == CreatedGivesStates.manage_channels.state:
        state_data = await state.get_data()
        if state_data.get('give_callback_value'):
            await show_selected_give(
                jam=jam,
                state=state,
                give_callback_value=state_data['give_callback_value']
            )
        else:
            await jam.message.edit_text(
                start_text,
                reply_markup=kb_admin_menu
            )
            await state.finish()

    elif current_state == CreatedGivesStates.add_channel.state:
        await process_manage_channels(
            jam=jam
        )

    elif current_state == CreatedGivesStates.show_connected_channel.state:
        state_data = await state.get_data()
        give_callback_value = state_data.get('give_callback_value', False)
        markup = await TelegramChannel().get_keyboard(
            owner_id=jam.from_user.id,
            give_callback_value=give_callback_value
        )

        if markup:
            markup.add(bt_admin_cancel_action)
            await jam.message.edit_text(
                '📢 <b>Ko‘rish uchun kanalni tanlang:</b>',
                reply_markup=markup
            )
            await CreatedGivesStates.select_connected_channel.set()
        else:
            await process_manage_channels(
                jam=jam
            )

    elif current_state == CreatedGivesStates.select_connected_channel.state:
        await process_manage_channels(
            jam=jam
        )

    else:
        await jam.message.edit_text(
            start_text,
            reply_markup=kb_admin_menu
        )
        await state.finish()


@dp.message_handler(
    text=['❌ Bekor qilish', '/cancel'],
    state='*'
)
async def cancel_message_action(jam: types.Message, state: FSMContext):
    await state.finish()
    await jam.answer(
        '🔙 <b>Amal bekor qilindi!</b>\nAsosiy boshqaruv menyusidasiz.',
        reply_markup=kb_main_menu
    )
    await jam.answer(
        start_text,
        reply_markup=kb_admin_menu
    )
