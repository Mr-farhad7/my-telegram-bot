# Telegram Repost Bot

یک ربات تلگرام برای انتقال خودکار محتوا بین کانال‌ها با قابلیت حذف لینک‌ها

## ویژگی‌ها
- انتقال خودکار پست‌ها از کانال مبدا به مقصد
- حذف خودکار لینک‌ها و mentions
- تاخیر تصادفی 7-12 دقیقه‌ای بین ارسال
- جلوگیری از ارسال duplicate با سیستم دیتابیس

## نصب و راه‌اندازی
1. کلون کردن ریپازیتوری:
   ```bash
   git clone https://github.com/username/telegram-repost-bot.git
   ```

2. نصب dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. تنظیم متغیرهای محیطی:
   - `BOT_TOKEN`: توکن ربات تلگرام
   - `SOURCE_CHANNEL`: آیدی کانال مبدا
   - `DEST_CHANNEL`: آیدی کانال مقصد
