"""
Render va boshqa platformalar uchun qo'shimcha ishga tushirish fayli.
"""
import asyncio

# Python 3.10+ / 3.12+ / 3.14+ (Render Linux) uchun event loop sozlamasi
try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        raise RuntimeError
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

import app

if __name__ == '__main__':
    from app import dp, on_startup, on_shutdown, executor
    executor.start_polling(
        dp,
        loop=loop,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )
