import asyncio
import re
from typing import Union
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BotBlocked, UserDeactivated, ChatNotFound, RetryAfter

from app import bot, dp
from config import OWNERS
from database import BotUser
from keyboards.admin.inline.owner_menu import (
    kb_broadcast_buttons_opt,
    kb_broadcast_confirm
)
from states.owner import OwnerStates


@dp.callback_query_handler(text='owner_broadcast', state='*')
async def owner_start_broadcast(jam: types.CallbackQuery, state: FSMContext):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    await state.finish()
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Bekor qilish', callback_data='broad_cancel')
    )
    await jam.message.edit_text(
        "📢 <b>XABAR TARQATISH (RASSILKA)</b>\n\n"
        "Barcha bot foydalanuvchilariga yubormoqchi bo‘lgan xabaringizni yuboring ⬇️\n\n"
        "💡 <i>Har qanday turdagi xabar qabul qilinadi: oddiy matn, rasm, video, fayl yoki boshqa kanaldan forward.</i>",
        reply_markup=markup
    )
    await OwnerStates.broadcast_get_message.set()


@dp.callback_query_handler(text='broad_cancel', state='*')
async def owner_cancel_broadcast(jam: types.CallbackQuery, state: FSMContext):
    await state.finish()
    from keyboards.admin.inline.owner_menu import kb_owner_panel
    await jam.message.edit_text(
        "🚫 <b>Xabar tarqatish bekor qilindi.</b>\n\n"
        "👑 <b>BOT EGASI BOSHQARUV PANELI:</b>",
        reply_markup=kb_owner_panel
    )
    await OwnerStates.main_menu.set()


@dp.message_handler(state=OwnerStates.broadcast_get_message, content_types=types.ContentTypes.ANY)
async def owner_receive_broadcast_msg(jam: types.Message, state: FSMContext):
    if jam.from_user.id not in OWNERS:
        return

    await state.update_data(
        from_chat_id=jam.chat.id,
        message_id=jam.message_id
    )

    await jam.answer(
        "🔘 <b>Xabarga tugma (havola) qo‘shilsinmi?</b>\n\n"
        "Agar tugma qo‘shmoqchi bo‘lsangiz «➕ Tugma qo‘shish»ni bosing, "
        "aks holda «⏩ Tugmasiz davom etish»ni bosing:",
        reply_markup=kb_broadcast_buttons_opt
    )


@dp.callback_query_handler(text='broad_add_btn', state=OwnerStates.broadcast_get_message)
async def owner_ask_broadcast_button(jam: types.CallbackQuery, state: FSMContext):
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🔙 Bekor qilish', callback_data='broad_cancel')
    )
    await jam.message.edit_text(
        "🔗 <b>Tugma ma’lumotlarini kiriting:</b>\n\n"
        "Format: <code>Tugma nomi | https://manzil.com</code>\n\n"
        "<i>Misol: Kanalimizga obuna bo‘ling | https://t.me/kanal_nomi</i>",
        reply_markup=markup
    )
    await OwnerStates.broadcast_get_button.set()


@dp.message_handler(state=OwnerStates.broadcast_get_button)
async def owner_receive_broadcast_button(jam: types.Message, state: FSMContext):
    if jam.from_user.id not in OWNERS:
        return

    text = jam.text.strip()
    if '|' not in text:
        await jam.answer(
            "⚠️ <b>Format noto‘g‘ri!</b>\nIltimos, quyidagi formatda kiriting:\n"
            "<code>Tugma nomi | https://havola.com</code>"
        )
        return

    parts = text.split('|', 1)
    btn_text = parts[0].strip()
    btn_url = parts[1].strip()

    if not re.match(r'^https?://', btn_url):
        await jam.answer("⚠️ <b>Havola manzili https:// bilan boshlanishi kerak!</b>")
        return

    await state.update_data(
        button_text=btn_text,
        button_url=btn_url
    )

    await show_broadcast_preview(jam, state)


@dp.callback_query_handler(text='broad_skip_btn', state=OwnerStates.broadcast_get_message)
async def owner_skip_broadcast_button(jam: types.CallbackQuery, state: FSMContext):
    await show_broadcast_preview(jam, state)


async def show_broadcast_preview(jam: Union[types.Message, types.CallbackQuery], state: FSMContext):
    data = await state.get_data()
    from_chat_id = data['from_chat_id']
    msg_id = data['message_id']
    btn_text = data.get('button_text')
    btn_url = data.get('button_url')

    preview_markup = InlineKeyboardMarkup()
    if btn_text and btn_url:
        preview_markup.add(InlineKeyboardButton(text=btn_text, url=btn_url))

    user_id = jam.from_user.id
    await bot.send_message(user_id, "🔍 <b>XABARNING KORINISHI (PREVIEW):</b>")

    await bot.copy_message(
        chat_id=user_id,
        from_chat_id=from_chat_id,
        message_id=msg_id,
        reply_markup=preview_markup if btn_text else None
    )

    total_users = await BotUser.get_total_count()
    await bot.send_message(
        user_id,
        f"👥 <b>Qabul qiluvchilar soni:</b> <code>{total_users} nafar</code>\n\n"
        "Xabar barcha foydalanuvchilarga yuborilsinmi?",
        reply_markup=kb_broadcast_confirm
    )
    await OwnerStates.broadcast_confirm.set()


@dp.callback_query_handler(text='broad_confirm_send', state=OwnerStates.broadcast_confirm)
async def owner_execute_broadcast(jam: types.CallbackQuery, state: FSMContext):
    if jam.from_user.id not in OWNERS:
        await jam.answer("🚫 Ruxsat berilmagan!", show_alert=True)
        return

    data = await state.get_data()
    await state.finish()

    from_chat_id = data['from_chat_id']
    msg_id = data['message_id']
    btn_text = data.get('button_text')
    btn_url = data.get('button_url')

    reply_markup = InlineKeyboardMarkup()
    if btn_text and btn_url:
        reply_markup.add(InlineKeyboardButton(text=btn_text, url=btn_url))

    user_ids = await BotUser.get_all_ids()
    total = len(user_ids)

    if total == 0:
        await jam.message.edit_text("⚠️ <b>Botda hali xabar yuboriladigan foydalanuvchilar mavjud emas!</b>")
        return

    status_msg = await jam.message.edit_text(f"⏳ <b>Xabar tarqatish boshlandi...</b> (0 / {total})")

    sent = 0
    failed = 0

    for idx, uid in enumerate(user_ids, 1):
        try:
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=from_chat_id,
                message_id=msg_id,
                reply_markup=reply_markup if btn_text else None
            )
            sent += 1
        except (BotBlocked, UserDeactivated, ChatNotFound):
            failed += 1
            await BotUser.mark_blocked(uid)
        except RetryAfter as e:
            await asyncio.sleep(e.timeout)
            try:
                await bot.copy_message(
                    chat_id=uid,
                    from_chat_id=from_chat_id,
                    message_id=msg_id,
                    reply_markup=reply_markup if btn_text else None
                )
                sent += 1
            except Exception:
                failed += 1
        except Exception:
            failed += 1

        # Har 50 ta xabarda status yangilash
        if idx % 50 == 0 or idx == total:
            try:
                await status_msg.edit_text(
                    f"⏳ <b>Xabar tarqatilmoqda...</b>\n\n"
                    f"📤 Jarayon: <code>{idx} / {total}</code>\n"
                    f"✅ Yetkazildi: <code>{sent} ta</code>\n"
                    f"❌ Bloklangan: <code>{failed} ta</code>"
                )
            except Exception:
                pass

        await asyncio.sleep(0.04)

    from keyboards.admin.inline.owner_menu import kb_owner_panel
    await bot.send_message(
        jam.from_user.id,
        f"🎉 <b>XABAR TARQATISH YAKUNLANDI!</b> ✅\n\n"
        f"📊 <b>Natijalar:</b>\n"
        f"  • ✅ Yetkazildi: <code>{sent} nafar</code>\n"
        f"  • ❌ Yetib bormadi (bloklagan): <code>{failed} nafar</code>\n"
        f"  • 📦 Jami foydalanuvchilar: <code>{total} nafar</code>",
        reply_markup=kb_owner_panel
    )
