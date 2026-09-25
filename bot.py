import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time
import os
from flask import Flask

# Flask dummy server for Render port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "PK VIP Panel Bot is alive and running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Start web server in background thread
web_thread = threading.Thread(target=run_web)
web_thread.start()

# Tera Bot Token
TOKEN = "8586594224:AAEC6xF5L-NH6RJdcS2_Z0wjfQwzQ1f7YUs"
bot = telebot.TeleBot(TOKEN)

# Teri Real Telegram Admin ID
ADMIN_ID = 5815908284

# Apna VIP Channel ID yahan daal
CHANNEL_ID = -1001234567890 

# WhatsApp Channel Link (Feedback & Updates)
FEEDBACK_CHANNEL_LINK = "https://whatsapp.com/channel/0029Vb8Gfne7tkjCs7A3sf2a"
UPI_PAYMENT_LINK = "https://t.me/setupvideopk" # Payment ya bot contact link

# 1. Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 **Welcome to PK VIP Panel Store!**\n\n"
        "💳 **To get VIP Access:**\n"
        "1. Pay the required amount on our QR/UPI (₹20 for 1 Hour / ₹99 for 7 Days).\n"
        "2. Send the **Payment Screenshot** right here in this chat.\n\n"
        "Admin will verify and send your access link shortly!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# 2. Handle Payment Screenshot
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ Approve (1 Hour)", callback_data=f"app1h_{user_id}"),
        InlineKeyboardButton("✅ Approve (7 Days)", callback_data=f"app7d_{user_id}")
    )
    markup.row(
        InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")
    )

    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(
        ADMIN_ID,
        f"⚠️ **New Payment Proof Received!**\n👤 From: @{username} (ID: `{user_id}`)",
        reply_markup=markup,
        parse_mode="Markdown"
    )

    bot.reply_to(message, "⏳ Your payment proof has been sent to admin. Please wait for verification.")

# 3. Expiry Function (Auto Kick & Professional English Expiry Notice with WhatsApp Channel)
def expire_user_access(user_id, duration_seconds):
    time.sleep(duration_seconds)
    try:
        # Channel se remove karna
        bot.ban_chat_member(CHANNEL_ID, user_id)
        bot.unban_chat_member(CHANNEL_ID, user_id)

        # Professional English Expiry Message with Styling & WhatsApp Channel Button
        expiry_markup = InlineKeyboardMarkup()
        expiry_markup.row(InlineKeyboardButton("💳 Renew Access (₹20 / ₹99)", url=UPI_PAYMENT_LINK))
        expiry_markup.row(InlineKeyboardButton("📢 WhatsApp Channel", url=FEEDBACK_CHANNEL_LINK))

        expiry_message = (
            "⚠️ **ACCESS EXPIRED!** ⚠️\n\n"
            "Your VIP panel access period has successfully ended, and you have been removed from the channel.\n\n"
            "🔄 **Want to continue gaming without interruption?**\n"
            "You can easily renew your subscription by paying just **₹20** (1 Hour) or **₹99** (7 Days) and sending the screenshot again.\n\n"
            "💬 Join our WhatsApp channel for updates, proof, and feedback!"
        )
        bot.send_message(user_id, expiry_message, reply_markup=expiry_markup, parse_mode="Markdown")
    except Exception as e:
        print(f"Error kicking user: {e}")

# 4. Admin Action Handler (Approve / Reject)
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data
    parts = data.split("_")
    action = parts[0]
    target_user_id = int(parts[1])

    if action == "app1h":
        duration = 3600
        bot.send_message(target_user_id, "🎉 Your payment is approved for **1 Hour**! Here is your VIP Access Link: https://t.me/setupvideopk", parse_mode="Markdown")
        bot.answer_callback_query(call.id, "Approved for 1 Hour!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        threading.Thread(target=expire_user_access, args=(target_user_id, duration)).start()

    elif action == "app7d":
        duration = 604800
        bot.send_message(target_user_id, "🎉 Your payment is approved for **7 Days**! Here is your VIP Access Link: https://t.me/pkallmods", parse_mode="Markdown")
        bot.answer_callback_query(call.id, "Approved for 7 Days!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        threading.Thread(target=expire_user_access, args=(target_user_id, duration)).start()

    elif action == "rej":
        bot.send_message(target_user_id, "❌ Your payment proof was rejected. Please check your payment and send a valid screenshot.")
        bot.answer_callback_query(call.id, "Rejected!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

# Bot Run
print("Advanced VIP Bot with Expiry & WhatsApp Channel is running...")
bot.infinity_polling()
        
