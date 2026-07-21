import os
import random
import logging
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ARCHIVE_CHANNEL = -1004459815440           # کانال آرشیو (همان کانال خودت)

# 🔒 کانال‌هایی که کاربر باید عضو آن‌ها باشد (می‌توانی تعدادشان را کم یا زیاد کنی)
FORCE_JOIN_CHANNELS = [
    "@spark_news_tel",      # ← هر کانال دیگری هم خواستی اضافه کن
    # "@Spark_rap",
    # "@Spark_sport",
    # "@Spark_hotdog"
]

# لیست ۵۱ پست اولیه (ثابت در کد)
EXISTING_POSTS = [
    165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151,
    150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136,
    135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121,
    120, 119, 118, 117, 116, 1
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)
new_posts = []   # پست‌های جدیدی که از زمان اجرا به کانال آرشیو اضافه می‌شوند

# ---------------- ابزارهای کمکی ----------------
def is_member(user_id):
    """بررسی می‌کند که کاربر در تمام کانال‌های اجباری عضو باشد"""
    for ch in FORCE_JOIN_CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            logger.error(f"خطا در بررسی عضویت {ch}: {e}")
            return False
    return True

def join_keyboard():
    """ساخت کیبورد شیشه‌ای با لینک کانال‌ها + دکمهٔ تأیید"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    # دکمه برای هر کانال
    for ch in FORCE_JOIN_CHANNELS:
        # می‌توانی اسم دکمه را متناسب با کانال تنظیم کنی
        btn = types.InlineKeyboardButton(text=f"📢 {ch.replace('@', '')}", url=f"https://t.me/{ch.replace('@', '')}")
        markup.add(btn)
    # دکمهٔ تأیید عضویت
    markup.add(types.InlineKeyboardButton(text="🔄 تأیید عضویت", callback_data="check_join"))
    return markup

def get_two_random():
    all_posts = EXISTING_POSTS + new_posts
    if len(all_posts) < 2:
        return []
    return random.sample(all_posts, 2)

def send_random_posts(chat_id):
    """ارسال دو پست رندوم از کانال آرشیو به کاربر"""
    ids = get_two_random()
    if not ids:
        bot.send_message(chat_id, "هنوز دو پست توی کانال آرشیو ذخیره نشده. 🙁")
        return
    for msg_id in ids:
        try:
            bot.forward_message(chat_id=chat_id, from_chat_id=ARCHIVE_CHANNEL, message_id=msg_id)
        except Exception as e:
            logger.error(f"خطا در فوروارد {msg_id}: {e}")
            bot.send_message(chat_id, f"خطا در ارسال پست {msg_id}.")

# ---------------- دستورات ربات ----------------
@bot.message_handler(commands=['start'])
def start(message):
    if not is_member(message.from_user.id):
        # کاربر عضو نیست → نمایش پیام با دکمه‌های عضویت
        bot.send_message(
            message.chat.id,
            "🔒 برای دریافت پست‌های رندوم، باید عضو کانال‌های زیر باشید:",
            reply_markup=join_keyboard()
        )
        return

    # کاربر عضو است → ارسال مستقیم پست‌ها
    send_random_posts(message.chat.id)

# دکمهٔ تأیید عضویت
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    if is_member(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ عضویت شما تأیید شد. در حال دریافت پست‌ها...")
        # حذف کیبورد قبلی
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except:
            pass
        send_random_posts(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو همه کانال‌ها نشده‌اید!", show_alert=True)

# ---------------- سایر امکانات ----------------
@bot.message_handler(commands=['count'])
def count(message):
    total = len(EXISTING_POSTS) + len(new_posts)
    bot.reply_to(message, f"📊 تعداد پست‌های ذخیره‌شده: {total}")

@bot.channel_post_handler(func=lambda m: True)
def handle_new_post(message):
    new_posts.append(message.message_id)
    logger.info(f"✅ پست جدید به آرشیو اضافه شد: {message.message_id}")

# ---------------- اجرا ----------------
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("متغیر BOT_TOKEN تنظیم نشده!")
    bot.remove_webhook()
    logger.info("🚀 ربات با موفقیت اجرا شد. /start را بزنید.")
    bot.infinity_polling(skip_pending=True)
