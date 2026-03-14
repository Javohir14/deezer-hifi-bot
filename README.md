# Deezer Hi-Fi (FLAC) Telegram Bot

Ushbu bot orqali siz Deezer platformasidan yuqori sifatdagi Hi-Fi (FLAC) formatidagi musiqalarni Telegram qabul qilishingiz mumkin.

## O'rnatish bo'yicha qo'llanma

### 1. Talablar
- Python 3.9+ o'rnatilgan bo'lishi kerak.
- Yuqori sifatli (FLAC) musiqalarni yuklash uchun aktiv **Deezer Premium/Hi-Fi** akkaunti (aniqrog'i `arl` cookie) kerak. Uni qanday olish haqida pastroqda o'qiysiz.

### 2. O'rnatish
Ushbu loyiha papkasiga o'ting va kerakli kutubxonalarni o'rnating:

```bash
pip install -r requirements.txt
```

### 3. Sozlamalar (Configuration)
Loyiha ichidagi `.env.example` faylini nuxsalab (yoki nomini o'zgartirib) `.env` faylini hosil qiling.

`.env` fayli ichiga quyidagilarni kiriting:
- `BOT_TOKEN` = BotFather'dan olingan bot tokenini yozing.
- `DEEZER_ARL` = Deezer.com dagi `arl` cookie faylini yozing:
  **Qanday olinadi?** 
  1. Kompyuter brauzeridan deezer.com ga kiring va profilingizga login qiling.
  2. F12 (Developer tools) -> Application / Storage -> Cookies ga kiring.
  3. `arl` nomli qatorni toping va uning Value (Qqiymatini) ko'chirib oling (uzun harf/raqamlar).
  4. Nusxalangan kodni `.env` faylidagi `DEEZER_ARL=` dan keyin yozing.

*(Agar Deezer ARL topa olmasangiz internet orqali "How to get Deezer ARL" deb qidirib ko'ring yoki bot FLAC o'rniga pastroq sifatdagi musiqalarni yuklashi mumkin).*

### 4. Botni ishga tushirish

Barcha sozlamalar yakunlangach, botni quyidagi buyruq orqali ishga tushiring:

```bash
python main.py
```

### Foydalanish
Telegramda botga start bering.
Va istalgan Deezer musiqa/albom/pleylist havolasini yuboring. Bot musiqalarni (FLAC sifatda) sizga yuboradi.
