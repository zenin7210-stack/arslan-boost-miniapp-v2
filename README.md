# Arslan Boost · Mini App va Telegram bot

Interfeysning mavjud dizayni, logotiplari, rejim kartalari va neonga oid intro saqlangan. Yuqori aniqlikdagi yuborilgan bannerdan foydalaniladi; til almashtirilganda bot tanlangan banner sozlamasini, interfeys esa tarjimani yangilaydi.

## Botni sozlash

1. `.env.example` faylidan `.env` yarating.
2. `BOT_TOKEN`, `ADMIN_ID`, `ADMIN_USERNAME` va `MINIAPP_URL` qiymatlarini to‘ldiring.
3. `UZCARD`, `HUMO`, `CARD_HOLDER` va `TERMINAL_INSTRUCTIONS` maydonlariga o‘zingizning rekvizitlaringizni yozing. Namunaviy karta raqamlari yoki soxta `file_id` ishlatmang.
4. Telegram Stars uchun `STARS_RATE_UZS` ni o‘zingiz belgilagan kurs bilan sozlang; `0` bo‘lsa Stars hisobi o‘chirilgan bo‘ladi.
5. `pip install -r requirements.txt` va `python bot.py` buyruqlari bilan ishga tushiring.

Mini App ichida karta, HUMO, terminal va Telegram Stars tanlovlari mavjud. Boost buyurtmasida balansni oldindan to‘ldirish talab qilinmaydi; hisobdan to‘lash ixtiyoriy. ID yoki nick 32 belgigacha talab qilinadi, qiymat serverda narx bilan birga tekshiriladi. To‘lov faqat Telegram `successful_payment` kelganda yoki administrator qo‘lda tasdiqlaganda balansga yoziladi.

## Telegram Premium keyword javoblari

Telegram Business uchun bot ulanishini @BotFather’da yoqing. So‘ng administrator hisobida **Settings → Telegram Business → Chatbots** bo‘limidan botni ulang va kerakli chatlarda javob berish huquqini bering. Foydalanuvchi tayyor xabardagi `#uzcard`, `#humo`, `#stars` yoki `#terminal` tegini yuborganda bot sozlangan javobni beradi. Karta va terminal rekvizitlari serverdagi `.env` faylidan olinadi; kodga kiritilmagan. Terminal ko‘rsatmasi yoki karta raqami bo‘sh bo‘lsa, bot rekvizitni o‘zi to‘qib chiqarmaydi va javob yubormaydi.

## Alohida joylashtirilgan Mini App

Mini App HTML/CSS/JS statik joylashtiriladi. `config.js` faylida `apiBaseUrl`, `supportUrl` va `botUrl` qiymatlarini ko‘rsating. Bot serveridagi `ALLOWED_ORIGIN` maydoniga ilovaning aniq HTTPS manzilini kiriting. Ruscha va o‘zbekcha HD bannerlar uchun `BANNER_URL_RU` va `BANNER_URL_UZ` orqali har bir tilga mos rasmni ulang. O‘zbekcha asosiy HD banner loyihaga qo‘shilgan; ruscha banner uchun alohida rasm kerak bo‘ladi.
