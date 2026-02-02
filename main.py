import os
from flask import Flask
from threading import Thread
from telebot import TeleBot, types

app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

def run(): app.run(host='0.0.0.0', port=8080)

# --- AAPKI DETAILS ---
API_ID = "37197223"
API_HASH = "3a43ae287a696ee9a6a82fb79f605b75"
BOT_TOKEN = "8253466345:AAH_aw8u34XAoj_Y_9uPnQgRn_PJGwXnM6s"

bot = TeleBot(BOT_TOKEN)

# --- CHANNEL LIST ---
CHANNELS = {
    "Main Chnl": "-1003641267601",
    "Hentai Tempest": "-1003625900383",
    "Tempest Index": "-1003537760606",
    "Tempest Group": "-1003574535419",
    "Aane Wala Anime": "-100332592074"
}

user_data = {}

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'video_note'])
def handle_msg(message):
    chat_id = message.chat.id
    # Message ko yaad rakhna (buttons ke saath)
    user_data[chat_id] = {
        'msg_id': message.message_id, 
        'selected': [],
        'markup': message.reply_markup # Original buttons yahan save honge
    }
    
    markup = create_menu(chat_id)
    bot.reply_to(message, "Rimiru, select karein kahan post karna hai:", reply_markup=markup)

def create_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    selected = user_data[chat_id]['selected']
    for name, cid in CHANNELS.items():
        status = "✅ " if cid in selected else ""
        markup.add(types.InlineKeyboardButton(text=f"{status}{name}", callback_data=f"t_{cid}"))
    markup.add(types.InlineKeyboardButton(text="🚀 CONFIRM & POST", callback_data="send"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("t_"))
def toggle(call):
    chat_id = call.message.chat.id
    cid = call.data.split("_")[1]
    if chat_id not in user_data: return
    
    if cid in user_data[chat_id]['selected']:
        user_data[chat_id]['selected'].remove(cid)
    else:
        user_data[chat_id]['selected'].append(cid)
    
    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=create_menu(chat_id))

@bot.callback_query_handler(func=lambda call: call.data == "send")
def final_send(call):
    chat_id = call.message.chat.id
    data = user_data.get(chat_id)
    
    if not data or not data['selected']:
        bot.answer_callback_query(call.id, "Kam se kam ek chuno!")
        return
        
    success_count = 0
    for cid in data['selected']:
        try:
            # copy_message use karte waqt original buttons (markup) pass kar rahe hain
            bot.copy_message(
                chat_id=cid, 
                from_chat_id=chat_id, 
                message_id=data['msg_id'],
                reply_markup=data['markup'] # Isse buttons copy honge
            )
            success_count += 1
        except Exception as e:
            print(f"Error: {e}")
            
    bot.edit_message_text(f"Done Rimiru! Post {success_count} channels par buttons ke saath bhej di gayi.", chat_id, call.message.message_id)
    del user_data[chat_id]

if __name__ == "__main__":
    # skip_pending=True se conflict kam hoga
    t = Thread(target=lambda: bot.infinity_polling(skip_pending=True))
    t.start()
    run()
