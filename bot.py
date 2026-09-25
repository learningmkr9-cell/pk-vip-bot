import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time

# Tera Bot Token
TOKEN = "8586594224:AAEC6xF5L-NH6RJdcS2_Z0wjfQwzQ1f7YUs"
bot = telebot.TeleBot(TOKEN)

# Teri Real Telegram Admin ID
ADMIN_ID = 5815908284

# Yahan apne Channel ya Group ki ID daalni hai jahan se user ko kick karna hai (jaise -100xxxxxxxxxx)
CHANNEL_ID = -1001234567890 

# 1. Jab koi /start dabayega
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Welcome to PK VIP Panel Store!\n\n"
        "💳 To get VIP Access:\n"
        "1. Pay the required amount on our QR/UPI.\n"
        "2. Send the **Payment Screenshot** right here in this chat.\n\n"
        "Admin will verify and send your access link shortly!"
    )
    bot.reply_to(message, welcome_text)

# 2. Jab koi screenshot/photo bhejega
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ Approve (1 Hour)", callback_data=f"app1h_{user_id}"),
        InlineKeyboardButton("✅ Approve (7 Days)", callback_data=f"app7d_{user_id}"),
    )
    markup.row(
        InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")
    )
    
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(
        ADMIN_ID, 
        f"🔔 New Payment Proof Received!\n👤 From: @{username} (ID: {user_id})", 
        reply_markup=markup
    )
    
    bot.reply_to(message, "⏳ Your payment proof has been sent to the admin for verification. Please wait!")

# 3. Faltu messages ignore karne ke liye
@bot.message_handler(func=lambda message: True)
def catch_all(message):
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Please send only your **Payment Screenshot** here. Text messages are not allowed.")

# 4. Timer function jo time khatam hone par user ko kick karega
def expire_user_access(user_id, duration_seconds):
    time.sleep(duration_seconds)
    try:
        # Channel se user ko ban/kick karna taaki link kaam na kare
        bot.ban_chat_member(CHANNEL_ID, user_id)
        bot.unban_chat_member(CHANNEL_ID, user_id) # Unban isliye karte hain taaki dobara pay karke aa sake
        
        # User ko English mein expiry ka message aur buy option bhejna
        expiry_message = (
            "⚠️ **YOUR PANEL TIME HAS EXPIRED!** ⚠️\n\n"
            "Your VIP access period is now over. You have been removed from the channel.\n\n"
            "💳 Want to continue? Please make a new payment and send the screenshot again to renew your plan:\n"
            "👉 [Yahan apna Buy / Payment Link ya QR daal dena]"
        )
        bot.send_message(user_id, expiry_message, parse_mode="Markdown")
    except Exception as e:
        print(f"Error kicking user: {e}")

# 5. Jab Tu (Admin) Approve ya Reject dabayega
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data
    parts = data.split("_")
    action = parts[0]
    target_user_id = int(parts[1])
    
    if action == "app1h":
        # 1 Ghante ka timer (3600 seconds)
        duration = 3600 
        bot.send_message(target_user_id, "🎉 Your payment is approved for **1 Hour**! Here is your VIP Access Link: [Yahan apna channel link daal dena]")
        bot.answer_callback_query(call.id, "Approved for 1 Hour!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        
        # Background thread mein timer chalu kar diya
        threading.Thread(target=expire_user_access, args=(target_user_id, duration)).start()

    elif action == "app7d":
        # 7 Din ka timer (7 * 24 * 60 * 60 = 604800 seconds)
        duration = 604800 
        bot.send_message(target_user_id, "🎉 Your payment is approved for **7 Days**! Here is your VIP Access Link: [Yahan apna channel link daal dena]")
        bot.answer_callback_query(call.id, "Approved for 7 Days!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        
        # Background thread mein timer chalu kar diya
        threading.Thread(target=expire_user_access, args=(target_user_id, duration)).start()
    
    elif action == "rej":
        bot.send_message(target_user_id, "❌ Your payment proof was rejected. Please check your payment and send a valid screenshot.")
        bot.answer_callback_query(call.id, "Rejected!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

# Bot start karne ke liye
print("Advanced VIP Bot with Expiry Timer is running...")
bot.infinity_polling()
