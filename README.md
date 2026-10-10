# 🎉 Konkurs Qil BOT

**Konkurs Qil BOT** — Telegram kanallari va guruhlarida turli tanlovlar hamda sovrinli o‘yinlarni tashkil etish, ishtirokchilarni yig‘ish va g‘oliblarni adolatli tanlash uchun mo‘ljallangan Telegram bot.

## ✨ Asosiy imkoniyatlar

### 🎁 1. Tanlov yaratish

Bot orqali turli parametrlar asosida tanlovlar yaratish mumkin:

- G‘oliblar sonini belgilash.
- Tanlovning tugash sanasi va vaqtini belgilash.
- Tanlov turini tanlash.
- Tanlov uchun matn yozish.
- Rasm yoki video qo‘shish.
- CAPTCHA orqali botlardan himoyalash.
- Tanlovni kerakli parametrlar asosida sozlash.

![Tanlov yaratish](https://i.postimg.cc/TPNx7QsV/2023-05-21-183002.png)

### 👥 2. Tanlovda ishtirok etish

Foydalanuvchilar tanlovda ikki xil usulda qatnashishlari mumkin:

- **Tugma orqali:** foydalanuvchi maxsus tugmani bosib tanlovda ishtirok etadi.
- **Izohlar orqali:** foydalanuvchi tanlov postiga izoh sifatida belgilangan kalit so‘zni yozadi.

![Tanlovda qatnashish](https://i.postimg.cc/WzGbHggs/2023-05-21-183546.png)

![Ishtirok etish tugmasi](https://i.postimg.cc/yx48jvJf/2023-05-21-183520.png)

### 🏆 3. G‘oliblarni aniqlash

Tanlov yakunlangach, bot belgilangan miqdordagi g‘oliblarni tanlaydi.

- G‘oliblarni aniqlash jarayonida ta’sirchan animatsiya namoyish etiladi.
- Tanlov natijalarini jonli efirda ko‘rsatish mumkin.
- G‘oliblarni tanlash jarayoni ishtirokchilar uchun shaffof tarzda namoyish etiladi.

![G‘oliblarni aniqlash](https://i.postimg.cc/2y8XsfB3/2023-05-21-183729.png)

![Tanlov natijalari](https://i.postimg.cc/dQ4f8DzC/2023-05-21-183833.png)

### 🔔 4. Eslatmalar va bildirishnomalar

- Foydalanuvchilarni tanlov yakunlanishi haqida ogohlantirish.
- Ishtirokchilarga tanlovda qatnashishga ulgurishlari uchun eslatmalar yuborish.

### 📊 5. Natijalarni e’lon qilish

Tanlov yakunlangach, g‘oliblar ro‘yxati e’lon qilinadi.

- Natijalar uchun alohida post joylashtiriladi.
- Postda **“Natijalarni tekshirish”** havolasi bo‘ladi.
- Ushbu havola orqali foydalanuvchilar botga o‘tib, g‘oliblar ro‘yxati va tanlov haqidagi boshqa ma’lumotlarni ko‘rishlari mumkin.

![Tanlov natijalarini tekshirish](https://i.postimg.cc/D08PQfXQ/2023-05-21-183950.png)

### 🛡️ 6. Ishtirokchilarni tekshirish

Tugma orqali tashkil etiladigan tanlovlarda CAPTCHA himoyasini yoqish mumkin.

Bu imkoniyat avtomatik botlar ishtirokini kamaytirishga va haqiqiy foydalanuvchilarni tekshirishga yordam beradi.

### 📢 7. Tanlov kanallarini sozlash

Botga tanlovlar o‘tkaziladigan kanallarni qo‘shish mumkin.

- Qo‘shilgan kanallardan keyingi tanlovlarda foydalanish mumkin.
- Izohlar orqali tanlov o‘tkazish uchun kanalga tegishli guruh ham sozlanishi kerak.
- Kanal va guruh sozlamalari orqali tanlovlarni boshqarish mumkin.

![Kanal sozlamalari](https://i.postimg.cc/wM19NC6F/2023-05-25-165444.png)

![Kanalni sozlash](https://i.postimg.cc/QCk4mbjP/2023-05-25-165506.png)

### ✏️ 8. Tanlovni tahrirlash

Tanlov davomiyligini o‘zgartirish imkoniyati mavjud.

- Tanlov tugash sanasini o‘zgartirish.
- Tanlov muddatini uzaytirish yoki qisqartirish.

![Tanlov muddatini tahrirlash](https://i.postimg.cc/Cdp0BJmQ/2023-05-25-182535.png)

### ⚠️ 9. Xatoliklar haqida xabar berish

Kutilmagan xatolik yuz berganda, bot xatolik tafsilotlarini konfiguratsiyada ko‘rsatilgan bot egalari yoki administratorlariga yuboradi.

Bu muammolarni aniqlash va bartaraf etishni osonlashtiradi.

![Xatolik haqida xabar](https://i.postimg.cc/Nf6TGk7y/2023-05-25-194722.png)

---

## ⚙️ O‘rnatish

### 📌 Talablar

Botning to‘g‘ri ishlashi uchun quyidagilar talab etiladi:

- **Python:** 3.10–3.11
- **Ma’lumotlar bazasi:** PostgreSQL
- **Telegram bot tokeni:** BotFather orqali olingan token

### 1. Loyihani yuklab olish

GitHub repository manzilingizni quyidagi buyruqqa kiriting:

```bash
git clone REPOSITORY_MANZILI
```

Loyiha papkasiga o‘ting:

```bash
cd loyiha-papkasi
```

### 2. Konfiguratsiyani sozlash

`config/py_config.py` faylini oching va kerakli qiymatlarni kiriting:

```python
OWNERS = []  # Bot egalari Telegram ID raqamlari

bot_token = ''  # Telegram bot tokeni

database_url = ''  # PostgreSQL ma'lumotlar bazasi manzili
# Misol: postgresql://postgres:parol@localhost:5432/postgres

timezone_info = pytz.timezone('Asia/Tashkent')

start_text = 'Asosiy menyu: '

text_for_participation_in_comments_giveaways = 'Qatnashaman'
```

**Eslatma:** `OWNERS` ro‘yxatiga bot egalarining Telegram ID raqamlarini kiriting. `bot_token` maydoniga haqiqiy bot tokenini, `database_url` maydoniga esa PostgreSQL ulanish manzilini yozing. Tokenni ochiq GitHub repository’ga joylashtirmang.

### 3. Kerakli kutubxonalarni o‘rnatish

Terminalda quyidagi buyruqni bajaring:

```bash
pip install -r requirements.txt
```

### 4. Botni ishga tushirish

Barcha sozlamalar tayyor bo‘lgach, botni quyidagi buyruq bilan ishga tushiring:

```bash
python app.py
```

Agar konfiguratsiya va ma’lumotlar bazasi to‘g‘ri sozlangan bo‘lsa, bot ishga tushadi.

---

## 🗄️ Ma’lumotlar bazasi

Loyiha PostgreSQL ma’lumotlar bazasidan foydalanadi.

Ma’lumotlar bazasi manzili `config/py_config.py` faylidagi `database_url` parametrida belgilanadi.

Misol:

```text
postgresql://postgres:parol@localhost:5432/postgres
```

`parol` qiymatini o‘zingizning PostgreSQL parolingizga almashtiring.

## 🤝 Qo‘llab-quvvatlash

Loyiha bo‘yicha xatoliklar yoki texnik muammolar yuzaga kelsa, quyidagi manzillardan foydalanishingiz mumkin:

- **Telegram:** https://t.me/developer_muxa
- **Elektron pochta:** muxiddin980001@gmail.com

Iltimos, ushbu manzillarga faqat noma’lum xatoliklar yoki texnik muammolar yuzasidan murojaat qiling.

---

**Konkurs Qil BOT** — Telegram tanlovlarini yaratish, boshqarish va g‘oliblarni aniqlash uchun qulay yechim. 🎉
