import os
import asyncio
from aiohttp import web, ClientSession

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


async def handle_ping(request):
    """Render va Uptime monitoring (Cron-job, UptimeRobot) uchun health-check"""
    return web.json_response({
        "status": "ok",
        "service": "telegram-giveaway-bot",
        "active": True
    })


async def start_web_server():
    """Render Web Service portida HTTP serverni ko'tarish"""
    port_str = os.environ.get("PORT")
    if not port_str:
        return

    try:
        port = int(port_str)
        app_web = web.Application()
        app_web.router.add_get("/", handle_ping)
        app_web.router.add_get("/health", handle_ping)
        app_web.router.add_get("/ping", handle_ping)

        runner = web.AppRunner(app_web)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        print(f"🚀 Render HTTP Web Server {port}-portda ishga tushdi!")
    except Exception as e:
        print(f"⚠️ Web serverni ishga tushirishda xatolik: {e}")


async def keep_alive_self_ping():
    """Agar RENDER_EXTERNAL_URL yoki PING_URL berilgan bo'lsa, o'zini o'zi uyg'otib turadi"""
    url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("PING_URL")
    if not url:
        return

    ping_endpoint = f"{url.rstrip('/')}/ping"
    await asyncio.sleep(60)
    async with ClientSession() as session:
        while True:
            try:
                async with session.get(ping_endpoint, timeout=10) as resp:
                    print(f"🔄 Keep-alive ping yuborildi: {ping_endpoint} (status: {resp.status})")
            except Exception as e:
                print(f"⚠️ Keep-alive ping xatoligi: {e}")
            await asyncio.sleep(600)  # Har 10 daqiqada (Render 15 daqiqada uxlaydi)


async def on_startup(dispatcher):
    await initialize_database()
    await set_default_commands(dispatcher)
    asyncio.create_task(manage_active_giveaways())
    asyncio.create_task(start_web_server())
    asyncio.create_task(keep_alive_self_ping())


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
