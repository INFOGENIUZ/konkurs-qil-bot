import asyncio

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor
from aiogram.types import ParseMode, BotCommand
from tortoise import Tortoise

from config import *
from database import initialize_database


bot = Bot(
    token=bot_token,
    parse_mode=ParseMode.HTML
)

storage = MemoryStorage()
dp = Dispatcher(
    bot,
    storage=storage
)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand("start", "Botni ishga tushirish / Bosh menyu"),
        BotCommand("help", "Yordam va qo‘llanma"),
    ])


async def on_startup(dispatcher):
    await initialize_database()
    await set_default_commands(dispatcher)
    asyncio.create_task(manage_active_giveaways())


async def on_shutdown(dispatcher):
    await Tortoise.close_connections()


if __name__ == '__main__':
    from handlers import dp, manage_active_giveaways

    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )
