import os
import logging
import sqlite3
import re
import asyncio
import random
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# ==================== تنظیمات از متغیرهای محیطی ====================
TOKEN = os.environ.get("TOKEN", "7881185873:AAGeoxxuDin6Hh2NaN97Dq3AfFjAKE5Zaes")
SOURCE_CHANNEL = os.environ.get("SOURCE_CHANNEL", "@farhad78787878")
DEST_CHANNEL = os.environ.get("DEST_CHANNEL", "@farhad1234567891011")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "processed_messages.db")
# =====================================================

# ------ تنظیمات لاگ ------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ------ سیستم دیتابیس ------
def init_database():
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS processed (
                id INTEGER PRIMARY KEY,
                message_id INTEGER UNIQUE NOT NULL
            )
        ''')

def is_message_processed(message_id: int) -> bool:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.execute(
            "SELECT 1 FROM processed WHERE message_id = ?",
            (message_id,)
        )
        return cursor.fetchone() is not None

def mark_as_processed(message_id: int):
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.execute(
            "INSERT INTO processed (message_id) VALUES (?)",
            (message_id,)
        )

# ------ پردازش متن (ویرایش نهایی) ------
def process_content(text: str) -> str:
    # فقط لینک‌ها حذف شوند + آیدی کانال مقصد اضافه شود
    cleaned_text = re.sub(
        r'(https?://\S+)|(www\.\S+)|(t\.me/\S+)|(@\w+)', 
        '', 
        text, 
        flags=re.IGNORECASE
    )
    return f"{cleaned_text}\n\n🔗 {DEST_CHANNEL}" if cleaned_text.strip() else ""

# ------ هندلر اصلی (ویرایش نهایی) ------
async def channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.channel_post
        
        # بررسی هویت کانال مبدا
        if message.chat.username != SOURCE_CHANNEL.lstrip('@'):
            return

        if is_message_processed(message.message_id):
            logger.info(f"پیام تکراری {message.message_id} نادیده گرفته شد")
            return

        # ایجاد تاخیر تصادفی 7-12 دقیقه
        delay = random.randint(420, 720)
        await asyncio.sleep(delay)

        # پردازش محتوا
        content = message.caption if message.caption else message.text
        processed_content = process_content(content) if content else ""
        
        # جلوگیری از ارسال پیام خالی
        if not processed_content.strip():
            return

        # ارسال بر اساس نوع محتوا
        if message.photo:
            await context.bot.send_photo(
                chat_id=DEST_CHANNEL,
                photo=message.photo[-1].file_id,
                caption=processed_content
            )
        elif message.video:
            await context.bot.send_video(
                chat_id=DEST_CHANNEL,
                video=message.video.file_id,
                caption=processed_content
            )
        elif message.document:
            await context.bot.send_document(
                chat_id=DEST_CHANNEL,
                document=message.document.file_id,
                caption=processed_content
            )
        else:
            await context.bot.send_message(
                chat_id=DEST_CHANNEL,
                text=processed_content
            )

        mark_as_processed(message.message_id)
        logger.info(f"پیام {message.message_id} پس از {delay//60} دقیقه منتشر شد")

    except Exception as e:
        logger.error(f"خطا در پردازش پیام: {str(e)}", exc_info=True)

# ======= اجرای ربات =======
if __name__ == "__main__":
    init_database()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(
        filters.ChatType.CHANNEL & 
        (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL),
        channel_handler
    ))
    logger.info("ربات شروع به کار کرد...")
    app.run_polling()
