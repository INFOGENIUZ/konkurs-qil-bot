from aiogram import types
from aiogram.dispatcher import FSMContext
from app import dp
from database import GiveAwayStatistic, GiveAway
from keyboards import *
from states import ActiveGivesStates


@dp.callback_query_handler(
    text=bt_admin_show_statistic.callback_data,
    state=ActiveGivesStates.manage_selected_give
)
async def show_give_statistic(
    jam: types.CallbackQuery,
    state: FSMContext
):
    await ActiveGivesStates.show_statistic.set()
    state_data = await state.get_data()
    callback_value = state_data['give_callback_value']

    statistic_info = await GiveAwayStatistic().get_statistic(
        giveaway_callback_value=callback_value
    )

    give_data = await GiveAway().filter(callback_value=callback_value).first().values('name', 'winners_count')
    give_name = give_data['name'] if give_data else "Konkurs"
    winners_count = give_data['winners_count'] if give_data else 0

    if statistic_info:
        await jam.message.edit_text(
            f"📊 <b>KONKURS STATISTIKASI</b>\n\n"
            f"📌 <b>Nomi:</b> <code>{give_name}</code>\n"
            f"🟢 <b>Holati:</b> <i>Davom etmoqda</i>\n\n"
            f"📈 <b>Ishtirokchilar dinamikasi:</b>\n"
            f"  ⚡️ <b>Oxirgi 24 soatda:</b> <code>+{statistic_info.count_members_in_24_hours} ta</code>\n"
            f"  👥 <b>Jami ishtirokchilar:</b> <code>{statistic_info.count_members_summary} nafar</code>\n"
            f"  🏆 <b>Rejalashtirilgan g‘oliblar:</b> <code>{winners_count} nafar</code>\n\n"
            f"🔄 <i>Ma’lumotlar avtomatik tarzda real vaqt rejimida yangilanadi.</i>",
            reply_markup=kb_admin_cancel_action
        )

    else:
        await jam.answer('ℹ️ Konkursda hozircha ishtirokchilar ro‘yxatga olinmagan!')
