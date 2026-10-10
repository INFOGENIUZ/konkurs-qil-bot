from aiogram import types
from aiogram.dispatcher import FSMContext

from app import dp
from database import GiveAway, TelegramChannel, GiveAwayStatistic
from keyboards import (
    kb_admin_select_type_of_give,
    kb_admin_manage_channels,
    kb_admin_menu,
    kb_main_menu,
    bt_admin_cancel_action,
)
from states import CreatedGivesStates, ActiveGivesStates, CreateGiveStates
from config import start_text


@dp.message_handler(text=['🎁 Konkurs yaratish', '/new_giveaway', '/konkurs', '/yangi_konkurs'], state='*')
async def reply_create_give(jam: types.Message, state: FSMContext):
    await state.finish()
    await jam.answer(
        '🎁 <b>YANGI KONKURS YARATISH</b>\n\n'
        'Quyidagi formatlardan birini tanlang:\n\n'
        '🔘 <b>Tugma orqali</b> — ishtirokchilar "Qatnashish" tugmasini bosish orqali qatnashadi.\n'
        '💬 <b>Izohlar orqali</b> — post ostiga izoh qoldirganlar orasidan g‘olib aniqlanadi.\n\n'
        '👇 Tanlash uchun quyidagi tugmalardan birini bosing:',
        reply_markup=kb_admin_select_type_of_give
    )


@dp.message_handler(text=['📋 Yaratilgan konkurslar', '/created_giveaways', '/konkurslar'], state='*')
async def reply_created_gives(jam: types.Message, state: FSMContext):
    await state.finish()
    markup = await GiveAway().get_keyboard_of_created_gives(
        user_id=jam.from_user.id
    )

    if markup:
        markup.add(bt_admin_cancel_action)
        await jam.answer(
            '📋 <b>YARATILGAN KONKURSLAR</b>\n\n'
            'Boshqarish, tahrirlash yoki kanallarga chiqarish uchun kerakli konkursni tanlang:',
            reply_markup=markup
        )
        await CreatedGivesStates.select_give.set()
    else:
        await jam.answer(
            '⚠️ <b>Sizda hali ishga tushirilmagan konkurslar mavjud emas!</b>\n\n'
            'Yangi konkurs yaratish uchun «🎁 Konkurs yaratish» tugmasini bosing.'
        )


@dp.message_handler(text=['🚀 Faol konkurslar', '/active_giveaways', '/faol_konkurslar'], state='*')
async def reply_active_gives(jam: types.Message, state: FSMContext):
    await state.finish()
    markup = await GiveAway().get_keyboard_of_active_gives(
        user_id=jam.from_user.id
    )

    if markup:
        markup.add(bt_admin_cancel_action)
        await jam.answer(
            '🚀 <b>FAOL KONKURSLAR RO‘YXATI</b>\n\n'
            'Ayni paytda kanallarda davom etayotgan konkurslar.\n'
            'Batafsil ma’lumot yoki jonli statistika uchun tanlang:',
            reply_markup=markup
        )
        await ActiveGivesStates.select_give.set()
    else:
        await jam.answer(
            'ℹ️ <b>Hozircha faol (davom etayotgan) konkurslar mavjud emas!</b>'
        )


@dp.message_handler(text=['📢 Kanallarni boshqarish', '/channels'], state='*')
async def reply_manage_channels(jam: types.Message, state: FSMContext):
    await state.finish()
    await jam.answer(
        '📢 <b>KANALLARNI BOSHQARISH</b>\n\n'
        'Konkurslar o‘tkaziladigan homiy kanallarni sozlash bo‘limi.\n\n'
        'Kerakli amalni tanlang:',
        reply_markup=kb_admin_manage_channels
    )
    await CreatedGivesStates.manage_channels.set()


@dp.message_handler(text=['📊 Umumiy statistika', '/stats'], state='*')
async def reply_general_statistics(jam: types.Message, state: FSMContext):
    await state.finish()

    active_count = await GiveAway.filter(owner_id=jam.from_user.id, run_status=True).count()
    created_count = await GiveAway.filter(owner_id=jam.from_user.id, run_status=False).count()
    channels = await TelegramChannel.filter(owner_id=jam.from_user.id).all().values('channel_id')
    channels_count = len({ch['channel_id'] for ch in channels})

    owner_give_cbs = await GiveAway.filter(owner_id=jam.from_user.id).all().values('callback_value')
    cbs = [g['callback_value'] for g in owner_give_cbs]
    all_stats = await GiveAwayStatistic.filter(giveaway_callback_value__in=cbs).all().values('members') if cbs else []
    total_participants = sum(len(item['members']) for item in all_stats if item.get('members'))

    await jam.answer(
        f"📊 <b>UMUMIY STATISTIKA</b>\n\n"
        f"🎁 <b>Konkurslar ko‘rsatkichi:</b>\n"
        f"  • 🚀 Faol konkurslar: <code>{active_count} ta</code>\n"
        f"  • 📋 Kutilayotgan (yaratilgan): <code>{created_count} ta</code>\n"
        f"  • 📦 Jami konkurslar: <code>{active_count + created_count} ta</code>\n\n"
        f"📢 <b>Ulangan resurslar:</b>\n"
        f"  • Homiy kanallar soni: <code>{channels_count} ta</code>\n\n"
        f"👥 <b>Ishtirokchilar faolligi:</b>\n"
        f"  • Jami qatnashchilar: <code>{total_participants} nafar</code>\n\n"
        f"🕒 <i>Vaqt mintaqasi: Asia/Tashkent</i>"
    )
