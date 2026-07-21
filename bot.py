import os
import random
import logging
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1004459815440
FORCE_JOIN_CHANNEL = "@spark_news_tel"

EXISTING_POSTS = [
    165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151,
    150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136,
    135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121,
    120, 119, 118, 117, 116, 1
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)
new_posts = []

def is_member(user_id):
    try:
        member = bot.get_chat_member(FORCE_JOIN_CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except Exception as e:
        logger.error(f"خطا در بررسی عضویت کاربر {user_id}: {e}")
        return False

def get_two_random():
    all_posts = EXISTING_POSTS + new_posts
    if len(all_posts) < 2:
        return []
    return random.sample(all_posts, 2)

# ----- /start -----
@bot.message_handler(commands=['start'])
def start(message):
    if not is_member(message.from_user.id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_channel = types.InlineKeyboardButton("📢 Spark News", url="https://t.me/spark_news_tel")
        btn_check = types.InlineKeyboardButton("✅ تأیید عضویت", callback_data="check_join")
        markup.add(btn_channel, btn_check)
        bot.send_message(
            message.chat.id,
            "🔒 برای استفاده از ربات، لطفاً ابتدا در کانال زیر عضو شوید:",
            reply_markup=markup
        )
        return

    send_random_posts(message.chat.id, message.message_id)

def send_random_posts(chat_id, reply_to_msg_id=None):
    ids = get_two_random()
    if not ids:
        bot.send_message(chat_id, "هنوز دو پست توی کانال ذخیره نشده. 🙁")
        return
    for msg_id in ids:
        try:
            bot.forward_message(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_id=msg_id)
        except Exception as e:
            logger.error(f"خطا در فوروارد {msg_id}: {e}")
            bot.send_message(chat_id, f"خطا در ارسال پست {msg_id}.")

# ----- دکمهٔ تأیید عضویت -----
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    if is_member(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ عضویت شما تأیید شد.")
        # حذف دکمه‌ها
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except:
            pass
        send_random_posts(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو نشده‌اید. لطفاً ابتدا عضو کانال شوید.", show_alert=True)

# ----- /count -----
@bot.message_handler(commands=['count'])
def count(message):
    total = len(EXISTING_POSTS) + len(new_posts)
    bot.reply_to(message, f"📊 تعداد پست‌های ذخیره‌شده: {total}")

# ----- ذخیرهٔ پست‌های جدید کانال -----
@bot.channel_post_handler(func=lambda m: True)
def handle_new_post(message):
    new_posts.append(message.message_id)
    logger.info(f"✅ پست جدید اضافه شد: {message.message_id}")

# ----- اجرا -----
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("متغیر محیطی BOT_TOKEN تنظیم نشده!")
    bot.remove_webhook()
    logger.info("🚀 ربات با موفقیت اجرا شد. /start را بزنید.")
    bot.infinity_polling(skip_pending=True)
