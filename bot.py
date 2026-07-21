import os
import random
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ARCHIVE_CHANNEL = -1004459815440          # کانال آرشیو
FORCE_JOIN_USERNAME = "@spark_news_tel"   # فقط برای لینک دادن، نه برای چک کردن

EXISTING_POSTS = [
    165, 164, 163, 162, 161, 160, 159, 158, 157, 156, 155, 154, 153, 152, 151,
    150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136,
    135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124, 123, 122, 121,
    120, 119, 118, 117, 116, 1
]

bot = telebot.TeleBot(TOKEN)
new_posts = []

def get_two_random():
    all_posts = EXISTING_POSTS + new_posts
    if len(all_posts) < 2:
        return []
    return random.sample(all_posts, 2)

def send_posts(chat_id):
    ids = get_two_random()
    if not ids:
        bot.send_message(chat_id, "هنوز دو پست ذخیره نشده. 🙁")
        return False
    for msg_id in ids:
        try:
            bot.forward_message(chat_id=chat_id, from_chat_id=ARCHIVE_CHANNEL, message_id=msg_id)
        except Exception as e:
            bot.send_message(chat_id, f"خطا در ارسال پست {msg_id}.")
            return False
    return True

# /start
@bot.message_handler(commands=['start'])
def start(message):
    # مستقیم سعی کن پست‌ها رو بفرستی
    # اگر کاربر عضو کانال اجباری نباشه، فوروارد ناموفق می‌مونه (چون پست‌ها رو نمی‌بینه)
    success = send_posts(message.chat.id)
    if not success:
        # احتمالاً کاربر عضو نیست → پیام دعوت
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{FORCE_JOIN_USERNAME[1:]}"))
        markup.add(types.InlineKeyboardButton("🔄 تأیید عضویت", callback_data="confirm"))
        bot.send_message(
            message.chat.id,
            "🔒 برای دریافت پست‌ها باید عضو کانال زیر باشید:",
            reply_markup=markup
        )

# دکمه تأیید
@bot.callback_query_handler(func=lambda c: c.data == "confirm")
def confirm(call):
    # این بار دوباره سعی کن پست‌ها رو بفرستی
    success = send_posts(call.message.chat.id)
    if success:
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except:
            pass
        bot.answer_callback_query(call.id, "✅ در حال ارسال...")
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو کانال نشده‌اید!", show_alert=True)

# ذخیره پست‌های جدید از کانال آرشیو
@bot.channel_post_handler(func=lambda m: True)
def handle_new_post(message):
    new_posts.append(message.message_id)

if __name__ == "__main__":
    if not TOKEN:
        exit("BOT_TOKEN not set")
    bot.remove_webhook()
    print("ربات روشن شد.")
    bot.infinity_polling()
