import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app import bot, dp
from config import OWNERS
from database import MandatoryChannel
from keyboards.admin.inline.owner_menu import kb_mandatory_menu
from states.owner import OwnerStates


@dp.callback_query_handler(text='owner_mandatory', state='*')
async def owner_open_mandatory_menu(jam: types.CallbackQuery, state: FSMContext):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    await state.finish()
    channels = await MandatoryChannel.get_active_channels()
    text = (
        "🔐 <b>MAJBURIY OBUNA (HOMIY KANALLAR)</b>\n\n"
        "Ushbu bo‘limda botdan foydalanish uchun majburiy bo‘lgan kanallarni sozlashingiz mumkin.\n\n"
        f"📌 Hozirda faol homiy kanallar: <b>{len(channels)} ta</b>\n\n"
        "Kerakli amalni tanlang:"
    )
    await jam.message.edit_text(text, reply_markup=kb_mandatory_menu)


@dp.callback_query_handler(text='mand_list', state='*')
async def owner_list_mandatory_channels(jam: types.CallbackQuery):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    channels = await MandatoryChannel.get_active_channels()
    if not channels:
        await jam.answer("ℹ️ Hozirda hech qanday majburiy kanal ulanmagan!", show_alert=True)
        return

    markup = InlineKeyboardMarkup()
    for ch in channels:
        markup.add(
            InlineKeyboardButton(
                text=f"🗑 O‘chirish: {ch['name'][:20]}",
                callback_data=f"mand_del_{ch['id']}"
            )
        )
    markup.add(
        InlineKeyboardButton('🔙 Orqaga', callback_data='owner_mandatory')
    )

    await jam.message.edit_text(
        "📋 <b>ULANGAN HOMIY KANALLAR RO‘YXATI:</b>\n\n"
        "Kanalni majburiy obunadan chiqarish uchun uning ustiga bosing:",
        reply_markup=markup
    )


@dp.callback_query_handler(lambda c: c.data.startswith('mand_del_'), state='*')
async def owner_delete_mandatory_channel(jam: types.CallbackQuery):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    ch_pk = int(jam.data.replace('mand_del_', ''))
    await MandatoryChannel.delete_channel_by_id(ch_pk)
    await jam.answer("✅ Kanal majburiy ro‘yxatdan olib tashlandi!", show_alert=True)

    # Ro'yxatni yangilaymiz
    await owner_list_mandatory_channels(jam)


@dp.callback_query_handler(text='mand_add', state='*')
async def owner_prompt_add_mandatory_channel(jam: types.CallbackQuery):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    bot_data = await bot.get_me()
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Bekor qilish', callback_data='owner_mandatory')
    )

    await jam.message.edit_text(
        "➕ <b>YANGI HOMIY KANAL QO‘SHISH</b>\n\n"
        f"1️⃣ Botni (@{bot_data.username}) kanalingizga administrator qiling.\n"
        "2️⃣ Kanal havolasini yoki @username'ini yuboring:\n"
        "<i>(Masalan: https://t.me/kanal_nomi yoki @kanal_nomi)</i>",
        reply_markup=markup
    )
    await OwnerStates.add_mandatory_channel.set()


@dp.message_handler(state=OwnerStates.add_mandatory_channel)
async def owner_save_mandatory_channel(jam: types.Message, state: FSMContext):
    if jam.from_user.id not in OWNERS:
        return

    from handlers.admin.manage_created_giveaways.manage_channels.add_channel import extract_channel_target
    target = extract_channel_target(jam)

    if not target:
        await jam.answer("⚠️ Iltimos, kanal havolasi yoki @username'ini to‘g‘ri yuboring!")
        return

    try:
        chat = await bot.get_chat(target)
    except Exception:
        await jam.answer("🚫 Kanal topilmadi! Havola to‘g‘ri yozilganini tekshiring.")
        return

    if chat.type != 'channel':
        await jam.answer("🚫 Faqat Telegram kanal qabul qilinadi!")
        return

    try:
        member = await bot.get_chat_member(chat_id=chat.id, user_id=bot.id)
        if member.status not in ['administrator', 'creator']:
            await jam.answer(
                f"🚫 Bot «{chat.title}» kanalida administrator emas!\n"
                "Avval botni kanalingizga administrator qilib qo‘shing."
            )
            return

        # Invite link olish
        invite_link = None
        if chat.username:
            invite_link = f"https://t.me/{chat.username}"
        elif chat.invite_link:
            invite_link = chat.invite_link
        else:
            try:
                invite_link = await bot.export_chat_invite_link(chat.id)
            except Exception:
                invite_link = None

        await MandatoryChannel.add_channel(
            channel_id=chat.id,
            name=chat.title,
            invite_link=invite_link
        )

        await state.finish()
        await jam.answer(
            f"✅ <b>Kanal muvaffaqiyatli homiy qilib ulandi!</b>\n\n"
            f"📢 <b>Nomi:</b> «{chat.title}»\n"
            f"🔗 <b>Havola:</b> {invite_link or 'Mavjud emas'}\n\n"
            "Endi barcha yangi foydalanuvchilar botdan foydalanish uchun ushbu kanalga a’zo bo‘lishi so‘raladi.",
            reply_markup=kb_mandatory_menu
        )
    except Exception as e:
        await jam.answer(f"🚫 Xatolik yuz berdi: {e}")
