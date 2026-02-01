import os
from flask import Flask
from threading import Thread
from telebot import TeleBot, types

# Render health check server
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

def run(): app.run(host='0.0.0.0', port=8080)

# --- AAPKI DETAILS ---
API_ID = "37197223"
API_HASH = "3a43ae287a696ee9a6a82fb79f605b75"
BOT_TOKEN = "8253466345:AAH_aw8u34XAoj_Y_9uPnQgRn_PJGwXnM6s"

bot = TeleBot(BOT_TOKEN)

# --- CHANNEL LIST (Updated) ---
CHANNELS = {
    "Main Chnl": "-1003641267601",
    "Hentai Tempest": "-1003625900383",
    "Tempest Index": "-1003537760606",
    "Tempest Group": "-1003574535419",
    "Aane Wala Anime": "-100332592074"
}

user_data = {}

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'video_note'])
def handle_post_request(message):
    chat_id = message.chat.id
    # Store message reference
    user_data[chat_id] = {'msg_id': message.message_id, 'selected': []}
    
    markup = create_selection_menu(chat_id)
    bot.reply_to(message, "Rimiru, select karein kahan post karna hai:", reply_markup=markup)

def create_selection_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    selected_list = user_data[chat_id]['selected']
    
    for name, cid in CHANNELS.items():
        # Add checkmark if selected
        status = "✅ " if cid in selected_list else ""
        markup.add(types.InlineKeyboardButton(text=f"{status}{name}", callback_data=f"toggle_{cid}"))
    
    markup.add(types.InlineKeyboardButton(text="🚀 CONFIRM & POST", callback_data="execute_post"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_"))
def toggle_channel(call):
    chat_id = call.message.chat.id
    cid = call.data.split("_")[1]
    
    if chat_id not in user_data: return
    
    # Toggle logic
    if cid in user_data[chat_id]['selected']:
        user_data[chat_id]['selected'].remove(cid)
    else:
        user_data[chat_id]['selected'].append(cid)
    
    # Update menu
    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=create_selection_menu(chat_id))

@bot.callback_query_handler(func=lambda call: call.data == "execute_post")
def final_action(call):
    chat_id = call.message.chat.id
    data = user_data.get(chat_id)
    
    if not data or not data['selected']:
        bot.answer_callback_query(call.id, "Kam se kam ek channel chuniye!")
        return
    
    success_count = 0
    for cid in data['selected']:
        try:
            bot.copy_message(chat_id=cid, from_chat_id=chat_id, message_id=data['msg_id'])
            success_count += 1
        except Exception:
            pass
            
    bot.edit_message_text(f"Done Rimiru! Post {success_count} channels par bhej di gayi.", chat_id, call.message.message_id)
    del user_data[chat_id]

if __name__ == "__main__":
    # Start Bot in background and Flask in foreground
    t = Thread(target=lambda: bot.infinity_polling(timeout=20, long_polling_timeout=10))
    t.start()
    run()

