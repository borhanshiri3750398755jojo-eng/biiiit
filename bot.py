import os
import random
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------- تنظیمات ----------
TOKEN = os.getenv("BOT_TOKEN")
ARCHIVE_CHANNEL = -1004459815440          # کانال آرشیو (همان کانال خودت)
FORCE_JOIN_CHANNEL = "@spark_news_tel"    # کانال اجباری (می‌تونی لیست کنی)

# لیست ۵۱ پست اولیه
EXISTING_POSTS = [
    165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151,
    150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136,
    135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121,
    120, 119, 118, 117, 116, 1
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# حافظهٔ موقت برای پست‌های جدید
new_posts = []

# ---------- توابع کمکی ----------
async def is_member(user_id: int) -> bool:
    """بررسی می‌کند کاربر در کانال اجباری عضو باشد"""
    try:
        member = await bot.get_chat_member(FORCE_JOIN_CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except Exception as e:
        logger.error(f"خطا در بررسی عضویت: {e}")
        return False

def get_two_random():
    all_posts = EXISTING_POSTS + new_posts
    if len(all_posts) < 2:
        return []
    return random.sample(all_posts, 2)

def join_keyboard():
    """کیبورد شیشه‌ای با لینک کانال + دکمهٔ تأیید"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Spark News", url="https://t.me/spark_news_tel")],
            [InlineKeyboardButton(text="🔄 تأیید عضویت", callback_data="check_join")]
        ]
    )

async def send_random_posts(chat_id: int):
    """ارسال دو پست رندوم به کاربر"""
    ids = get_two_random()
    if not ids:
        await bot.send_message(chat_id, "هنوز دو پست توی کانال ذخیره نشده. 🙁")
        return
    for msg_id in ids:
        try:
            await bot.forward_message(
                chat_id=chat_id,
                from_chat_id=ARCHIVE_CHANNEL,
                message_id=msg_id
            )
        except Exception as e:
            logger.error(f"خطا در فوروارد {msg_id}: {e}")
            await bot.send_message(chat_id, f"خطا در ارسال پست {msg_id}.")

# ---------- دستورات ----------
@dp.message(CommandStart())
async def start(message: types.Message):
    if not await is_member(message.from_user.id):
        await message.answer(
            "🔒 برای دریافت پست‌های رندوم، ابتدا در کانال زیر عضو شوید:",
            reply_markup=join_keyboard()
        )
        return
    # کاربر عضو است → ارسال پست‌ها
    await send_random_posts(message.chat.id)

# ---------- دکمهٔ تأیید عضویت ----------
@dp.callback_query(lambda c: c.data == "check_join")
async def check_join(call: types.CallbackQuery):
    if not await is_member(call.from_user.id):
        await call.answer("❌ هنوز عضو نشده‌اید!", show_alert=True)
        return

    await call.answer("✅ عضویت تأیید شد. در حال دریافت پست‌ها...")
    # حذف کیبورد قبلی
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        pass
    await send_random_posts(call.message.chat.id)

# ---------- ذخیره پست‌های جدید کانال (ربات باید ادمین باشد) ----------
@dp.channel_post()
async def handle_new_post(message: types.Message):
    new_posts.append(message.message_id)
    logger.info(f"✅ پست جدید ذخیره شد: {message.message_id}")

# ---------- اجرا ----------
async def main():
    logger.info("🚀 ربات با aiogram اجرا شد. منتظر /start ...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
