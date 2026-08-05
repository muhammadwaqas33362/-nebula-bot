import telebot
from telebot import types
from flask import Flask, request
import os
import openai
import requests

TOKEN = os.environ.get("BOT_TOKEN")
AGENTROUTER_KEY = os.environ.get("AGENTROUTER_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
USDT_WALLET = "0x4390c186a0B2b08b9423240D0719D2696a190a22"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_state = {}
user_model = {}
last_media = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('💬 Chat AI', '🎨 Image', '🎬 Video')
    markup.add('🤖 Select AI Model')
    markup.add('💳 Buy $10 Lite', '💳 Buy $25 Pro')
    return markup

def back_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🔙 Back')
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "🚀 *Welcome to NebulaAI Pro* 🚀\n\n"
        "✅ 6 AI Models: GPT-5.5, GLM-5.2, Claude-4.6, Gemini-1.5\n"
        "✅ Image + Video Generation\n"
        "✅ Download HD Files\n"
        "✅ Lite $10/mo | Pro $25/mo\n"
        "3 Free messages hain jani",
        reply_markup=main_menu(), parse_mode="Markdown")
    user_model[message.chat.id] = "gpt-5.5"

@bot.message_handler(func=lambda m: m.text == '🤖 Select AI Model')
def select_model(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('GPT-5.5', 'GLM-5.2')
    markup.add('Claude 3.5', 'Gemini 1.5')
    markup.add('Qwen 2.5', 'GPT-3.5')
    markup.add('🔙 Back')
    bot.send_message(message.chat.id, "Konsa AI chahiye? 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['GPT-5.5','GLM-5.2','Claude 3.5','Gemini 1.5','Qwen 2.5','GPT-3.5'])
def set_model(message):
    models = {
        'GPT-5.5': 'gpt-5.5',
        'GLM-5.2': 'glm-5.2',
        'Claude 3.5': 'claude-opus-4-6', # AgentRouter ka sahi naam
        'Gemini 1.5': 'gemini-1.5-pro-latest', # AgentRouter ka sahi naam
        'Qwen 2.5': 'qwen2.5-72b-instruct',
        'GPT-3.5': 'gpt-3.5-turbo-0125'
    }
    user_model[message.chat.id] = models[message.text]
    bot.send_message(message.chat.id, f"✅ *{message.text}* set ho gaya\nModel: `{models[message.text]}`", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == '💬 Chat AI')
def chat_ai(message):
    user_state[message.chat.id] = "chat"
    bot.send_message(message.chat.id, "Ok jani pucho 🤖", reply_markup=back_menu())

@bot.message_handler(func=lambda m: m.text == '🎨 Image')
def img(message):
    user_state[message.chat.id] = "image"
    bot.send_message(message.chat.id, "Prompt bhejo image ke liye 🎨\nNote: Violence/NSFW/Celebrity block ho jayega", reply_markup=back_menu())

@bot.message_handler(func=lambda m: m.text == '🎬 Video')
def vid(message):
    user_state[message.chat.id] = "video"
    bot.send_message(message.chat.id, "Prompt bhejo video ke liye 🎬\nNote: Violence/NSFW/Celebrity block ho jayega", reply_markup=back_menu())

@bot.message_handler(func=lambda m: m.text == '💳 Buy $10 Lite')
def buy10(message):
    bot.send_message(message.chat.id, f"*Lite $10/mo*\n\nUSDT bhejo:\n`{USDT_WALLET}`\n\nPayment ke baad TXID bhejna", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == '💳 Buy $25 Pro')
def buy25(message):
    bot.send_message(message.chat.id, f"*Pro $25/mo*\n\nUSDT bhejo:\n`{USDT_WALLET}`\n\nPayment ke baad TXID bhejna", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == '📥 Download Image')
def download_img(message):
    url = last_media.get(message.chat.id, {}).get('image')
    if url: bot.send_photo(message.chat.id, url, caption="HD Image 📥")
    else: bot.send_message(message.chat.id, "Pehle image banao 😅")

@bot.message_handler(func=lambda m: m.text == '📥 Download Video')
def download_vid(message):
    url = last_media.get(message.chat.id, {}).get('video')
    if url:
        bot.send_message(message.chat.id, "HD Video download ho rahi...")
        video_data = requests.get(url)
        bot.send_video(message.chat.id, video_data.content)
    else: bot.send_message(message.chat.id, "Pehle video banao 😅")

@bot.message_handler(func=lambda m: m.text == '🔄 New Image')
def new_img(message): user_state[message.chat.id] = "image"; bot.send_message(message.chat.id, "Naya prompt bhejo")

@bot.message_handler(func=lambda m: m.text == '🔄 New Video')
def new_vid(message): user_state[message.chat.id] = "video"; bot.send_message(message.chat.id, "Naya prompt bhejo")

@bot.message_handler(func=lambda m: m.text == '🔙 Back')
def back(message): start(message)

@bot.message_handler(content_types=['text'])
def ai_reply(message):
    skip = ['💬 Chat AI','🎨 Image','🎬 Video','🤖 Select AI Model','💳 Buy $10 Lite','💳 Buy $25 Pro','🔙 Back','📥 Download Image','📥 Download Video','🔄 New Image','🔄 New Video']
    if message.text in skip: return

    state = user_state.get(message.chat.id, "chat")
    model = user_model.get(message.chat.id, "gpt-5.5")
    client = openai.OpenAI(api_key=AGENTROUTER_KEY, base_url="https://agentrouter.org/v1")

    try:
        if state == "chat":
            res = client.chat.completions.create(model=model, messages=[{"role":"user","content":message.text}])
            bot.send_message(message.chat.id, f"*Model: {model}*\n\n{res.choices[0].message.content}", parse_mode="Markdown")

        elif state == "image":
            bot.send_message(message.chat.id, "Image ban rahi hai... 30 sec ⏳")
            res = client.images.generate(model="dall-e-3", prompt=message.text, n=1, size="1024x1024")
            img_url = res.data[0].url
            last_media[message.chat.id] = {'image': img_url}
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('📥 Download Image', '🔄 New Image')
            markup.add('🔙 Back')
            bot.send_photo(message.chat.id, img_url, reply_markup=markup)

        elif state == "video":
            bot.send_message(message.chat.id, "Video ban rahi hai... 2-3 min ⏳")
            res = client.video.generate(model="kling-1.0", prompt=message.text)
            vid_url = res.data[0].url
            last_media[message.chat.id] = {'video': vid_url}
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('📥 Download Video', '🔄 New Video')
            markup.add('🔙 Back')
            video_data = requests.get(vid_url)
            bot.send_video(message.chat.id, video_data.content, reply_markup=markup)

    except Exception as e:
        error_msg = str(e).lower()
        if "content-blocked" in error_msg:
            bot.send_message(message.chat.id, "⚠️ *Prompt Blocked*\n\nJani ye prompt AgentRouter ne block kar diya.\nReason: Violence, NSFW, ya Celebrity ka naam.\n\nNaya safe prompt bhejo.", parse_mode="Markdown")
        elif "model" in error_msg:
            bot.send_message(message.chat.id, f"⚠️ *Model Error*\n\nYe model abhi available nahi hai.\n`{model}`\n\n`🤖 Select AI Model` se dusra try karo.", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"❌ Error:\n`{str(e)}`", parse_mode="Markdown")

    user_state[message.chat.id] = "chat"

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

@app.route("/")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/" + TOKEN)
    return "Webhook set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))get("PORT", 5000)))
