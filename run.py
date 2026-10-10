"""
Render va boshqa platformalar uchun qo'shimcha ishga tushirish fayli.
Bu fayl app.py ni chaqiradi.
"""
from app import dp, manage_active_giveaways, on_startup, on_shutdown, executor

if __name__ == '__main__':
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )
