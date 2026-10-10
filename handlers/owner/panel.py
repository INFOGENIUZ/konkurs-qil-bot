from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from config import OWNERS
from keyboards.admin.inline.owner_menu import kb_owner_panel
from states.owner import OwnerStates


@dp.message_handler(commands=['owner', 'panel'], state='*')
async def cmd_owner_panel(jam: types.Message, state: FSMContext):
    if jam.from_user.id not in OWNERS:
        return

    await state.finish()
    await jam.answer(
        "👑 <b>BOT EGASI BOSHQARUV PANELI</b>\n\n"
        "Xush kelibsiz! Ushbu panel orqali siz botning global statistikasi, "
        "ommaviy xabar tarqatish, homiy kanallar va barcha konkurslarni boshqarishingiz mumkin.\n\n"
        "👇 Kerakli bo‘limni tanlang:",
        reply_markup=kb_owner_panel
    )
    await OwnerStates.main_menu.set()


@dp.callback_query_handler(text='owner_back_to_panel', state='*')
async def callback_back_to_owner_panel(jam: types.CallbackQuery, state: FSMContext):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    await state.finish()
    await jam.message.edit_text(
        "👑 <b>BOT EGASI BOSHQARUV PANELI</b>\n\n"
        "👇 Kerakli bo‘limni tanlang:",
        reply_markup=kb_owner_panel
    )
    await OwnerStates.main_menu.set()


@dp.callback_query_handler(text='owner_back_to_main', state='*')
async def callback_back_to_main_menu(jam: types.CallbackQuery, state: FSMContext):
    await state.finish()
    from keyboards import kb_main_menu, kb_admin_menu
    await jam.message.delete()
    await jam.message.answer(
        "🎛 <b>Asosiy boshqaruv menyusiga qaytdingiz:</b>",
        reply_markup=kb_main_menu
    )
    await jam.message.answer(
        "Tezkor boshqaruv menyusi:",
        reply_markup=kb_admin_menu
    )
