import random

from typing import Dict
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import MessageNotModified

from database import GiveAwayStatistic


class Captcha:
    captcha_id = 0
    passed_captcha_users = []

    def __init__(self, choices: Dict[str, str] = None) -> None:
        if choices and isinstance(choices, dict):
            self.choices = choices
        else:
            self.choices = {
                "olma": "🍎",
                "avtomobil": "🚗",
                "kuchukcha": "🐶",
                "daraxt": "🌳",
                "kamalak": "🌈",
                "banan": "🍌",
                "telefon": "📱",
                "quyosh": "☀️",
                "shirinlik": "🍬",
                "to‘p": "⚽️",
                "soat": "⌚️",
                "stul": "🪑",
                "taqvim": "📆",
                "qulf": "🔒",
                "qulupnay": "🍓"
            }
        self.correct_choice = random.choice(list(self.choices.keys()))

        Captcha.captcha_id += 1
        self.captcha_id = Captcha.captcha_id
        self.callback_name = f"_Captcha{self.captcha_id}"

        self.captcha_passed = False

    def get_captcha_keyboard(self) -> InlineKeyboardMarkup:
        captcha_keyboard = InlineKeyboardMarkup()

        for choice in random.sample(list(self.choices.keys()), len(self.choices)):
            captcha_keyboard.insert(
                InlineKeyboardButton(
                    self.choices[choice],
                    callback_data=f"{self.callback_name}_choice_"
                    + ("1" if choice == self.correct_choice else "0")
                )
            )

        return captcha_keyboard

    def get_caption(self) -> str:
        return f"🤖 <b>Bot emassizligingizni tasdiqlang:</b>\n\n👇 Iltimos, <b>{self.correct_choice}</b> belgisini bosing:"

    async def captcha_choice_handler(
        self,
        callback_query: types.CallbackQuery,
        state: FSMContext
    ) -> None:
        if callback_query.data.split("_")[-1] == "0":
            self.correct_choice = random.choice(list(self.choices.keys()))
            try:
                await callback_query.message.edit_text(
                    f"❌ <b>Noto‘g‘ri tanlov!</b>\n\n👇 Iltimos, <b>{self.correct_choice}</b> belgisini bosing:",
                    reply_markup=self.get_captcha_keyboard(),
                )
            except MessageNotModified:
                ...
            return

        self.captcha_passed = True
        Captcha.passed_captcha_users.append(callback_query.from_user.id)

        state_data = await state.get_data()
        give_callback_value = state_data.get('give_callback_value')

        await callback_query.message.delete()

        updated = await GiveAwayStatistic().update_statistic_members(
            giveaway_callback_value=give_callback_value,
            new_member_username=callback_query.from_user.username,
            new_member_id=callback_query.from_user.id
        )

        if updated:
            from handlers.admin.functions_for_active_gives.update_channel_post import update_giveaway_post_buttons
            await update_giveaway_post_buttons(give_callback_value)

        from handlers.admin.functions_for_active_gives.handle_new_members_from_button_giveaways import send_participant_card
        await send_participant_card(
            user=callback_query.from_user,
            give_callback_value=give_callback_value,
            is_already=False
        )

    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(
            self.captcha_choice_handler,
            lambda c: c.data.startswith(f"{self.callback_name}_choice_"),
        )
