import re
from aiogram import types
from aiogram.dispatcher import FSMContext

from app import bot, dp
from database import TelegramChannel
from states import CreatedGivesStates
from keyboards import kb_admin_manage_channels, kb_admin_cancel_action


def extract_channel_target(message: types.Message) -> str | int | None:
    """Matndan kanal username, link yoki ID raqamini aniqlash"""
    # 1. Agar xabar matn bo'lsa
    text = (message.text or message.caption or '').strip()

    # Raqamli kanal ID (masalan: -1001234567890)
    if re.match(r'^-100\d+$', text):
        return int(text)

    # t.me/kanal_nomi yoki telegram.me/kanal_nomi havolalari
    link_match = re.search(r'(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/([a-zA-Z0-9_]+)', text)
    if link_match:
        username = link_match.group(1)
        if username not in ['joinchat', 'addstickers', 'c']:
            return f"@{username}"

    # @kanal_nomi format
    if text.startswith('@'):
        clean = text.lstrip('@').split('/')[0].strip()
        if re.match(r'^[a-zA-Z0-9_]{4,32}$', clean):
            return f"@{clean}"

    # To'g'ridan-to'g'ri kanal_nomi (min 4 belgi)
    if re.match(r'^[a-zA-Z0-9_]{4,32}$', text):
        return f"@{text}"

    # 2. Qo'shimcha xavfsizlik: agar tasodifan forward qilingan bo'lsa ham qabul qilish
    if message.forward_from_chat and message.forward_from_chat.type == 'channel':
        return message.forward_from_chat.id

    return None


@dp.message_handler(
    state=CreatedGivesStates.add_channel,
)
async def get_channel_data(
    jam: types.Message,
    state: FSMContext
):
    target = extract_channel_target(jam)

    if not target:
        await jam.answer(
            '⚠️ <b>Noto‘g‘ri havola yoki format!</b>\n\n'
            'Iltimos, kanal havolasini quyidagi formatlardan birida yuboring:\n'
            '• <code>https://t.me/kanal_nomi</code>\n'
            '• <code>@kanal_nomi</code>\n'
            '• <code>kanal_nomi</code>\n\n'
            '<i>Misol uchun: @texnouzbek yoki https://t.me/texnouzbek</i>',
            reply_markup=kb_admin_cancel_action
        )
        return

    try:
        chat = await bot.get_chat(target)
    except Exception:
        await jam.answer(
            '🚫 <b>Kanal topilmadi!</b>\n\n'
            'Iltimos, havola to‘g‘ri yozilganligini va bot avval ushbu kanalga qo‘shilganligini tekshiring.',
            reply_markup=kb_admin_cancel_action
        )
        return

    if chat.type != 'channel':
        await jam.answer(
            '🚫 <b>Bu kanal emas!</b>\n\n'
            'Iltimos, faqat Telegram kanal havolasini yuboring (guruh yoki shaxsiy profil qabul qilinmaydi).',
            reply_markup=kb_admin_cancel_action
        )
        return

    try:
        member_info = await bot.get_chat_member(
            chat_id=chat.id,
            user_id=bot.id
        )

        if member_info.status not in ['administrator', 'creator']:
            await jam.answer(
                f'🚫 <b>Xatolik!</b> Bot «{chat.title}» kanalida <b>administrator emas</b>.\n\n'
                f'Iltimos, avval botni kanalingizga administrator qilib qo‘shing va quyidagi huquqlarni bering:\n'
                f'  • <i>Xabarlarni yuborish (Post messages)</i>\n\n'
                f'So‘ngra kanal havolasini qayta yuboring:',
                reply_markup=kb_admin_cancel_action
            )
            return

        model = TelegramChannel()
        state_data = await state.get_data()
        give_callback_value = state_data.get('give_callback_value', '')

        if await model.exists_channel(
            channel_id=chat.id,
            give_callback_value=give_callback_value,
            owner_id=jam.from_user.id
        ):
            await jam.answer(
                f'⚠️ <b>«{chat.title}» kanali allaqachon ushbu konkursga qo‘shilgan!</b>\n\n'
                f'Iltimos, boshqa kanal havolasini yuboring:',
                reply_markup=kb_admin_cancel_action
            )
            return

        await model.add_channel(
            owner_id=jam.from_user.id,
            channel_id=chat.id,
            give_callback_value=give_callback_value,
            name=chat.title
        )

        ch_username = f"@{chat.username}" if chat.username else "Mavjud emas"
        await jam.answer(
            f'✅ <b>Kanal muvaffaqiyatli qo‘shildi!</b>\n\n'
            f'📢 <b>Nomi:</b> «{chat.title}»\n'
            f'🔗 <b>Havola:</b> {ch_username}\n'
            f'🆔 <b>ID:</b> <code>{chat.id}</code>',
            reply_markup=kb_admin_manage_channels
        )
        await CreatedGivesStates.manage_channels.set()

    except Exception as error:
        await jam.answer(
            f'🚫 <b>Xatolik yuz berdi:</b> {error}\n\n'
            'Bot kanal a’zosi va administratori ekanligiga ishonch hosil qiling va havolani qayta yuboring:',
            reply_markup=kb_admin_cancel_action
        )
